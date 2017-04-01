#!/usr/bin/env python
#
import os
import sys
from datetime import datetime
from datetime import timedelta
import yaml
import click

import clients

class CommandException(click.ClickException):
    pass

def load_config_file():
    config_file = os.path.expanduser('~/.evoc')
    if not os.path.isfile(config_file):
        raise CommandException('Config file ({}) not found'.format(config_file))
    return yaml.load(open(config_file))

def get_client():
    config = load_config_file()
    user = config['username']
    password = config['password']
    return clients.EvohomeControlClient(user, password)

def calculate_offset_time(minutes):
    if not minutes:
        return None
    return datetime.now() + timedelta(0, minutes*60)

def calculate_until_time(hours, minutes):
    now = datetime.now()
    time = datetime(2017,1,1,hours, minutes)
    end_time = datetime.combine(now.date(), time.time()) 
    if end_time < now:
        end_time = end_time + timedelta(1)
    return end_time

def get_until_time(duration, until):
    until_time = None
    if duration and until:
        raise CommandException('Specify only one of \'duration\' or \'until\'')
    if duration:
        if (duration < 10 or duration > 24 * 60):
            raise CommandException('duration must be 10 to 1440 minutes')
        until_time = calculate_offset_time(duration)
    elif until:
        until_time = calculate_until_time(until[0], until[1])
    return until_time

def temperature_range_check(ctx, param, value):
    if value == 'auto':
        return None
    try:
        value = float(value)
        if value < 0.0 or value > 30.0:
            raise click.BadParameter('temperature must be 0 - 30 degrees')
        return value
    except ValueError:
        raise click.BadParameter('temperature must be a number, or \'auto\'')

def check_and_convert_hh_mm(ctx, param, until):

    def check_range(val, low, high):
        if val < low or val > high: raise Exception()

    if until==None:
        return
    try:
        [hours, minutes] = [int(t) for t in until.split(':')]
        check_range(hours, 0, 23)
        check_range(minutes, 0, 59)
        return hours, minutes
    except:
        raise CommandException('Until time must be HH:MM format, where HH=0 to 23 and MM=0 to 59')

    
@click.group()
def cli():
    pass

@cli.command()
@click.argument('zone')
@click.argument('temperature', callback=temperature_range_check)
@click.option('--duration', type=int, help='Duration of override in minutes')
@click.option('--until', callback=check_and_convert_hh_mm, help='Local time in HH:MM to override until')
def zone(zone, temperature, duration, until):
    if temperature == 'auto' and (duration != None or until != None):
        raise CommandException('cannot specify duration in \'auto\' mode')
    try:
        until_time = get_until_time(duration, until)
        get_client().set_zone_temperature(zone, temperature, until_time)
    except KeyError:
        raise CommandException('Zone {} was not found'.format(zone))


def hw_mode_check(ctx, param, value):
    if not value in ['on', 'off', 'auto']:
        raise CommandException('Invalid mode')
    return value

def hotwater_on_off(client, state, duration_in_minutes=60):
    hotwater = client._get_single_heating_system().hotwater
    until_time = calculate_offset_time(duration_in_minutes)
    if state == 'on':
        hotwater.set_dhw_on(until_time)
    else:
        hotwater.set_dhw_off(until_time)

def hotwater_auto(client, state, duration_unused):
    client.set
    hotwater = client._get_single_heating_system().hotwater
    hotwater.set_dhw_auto()

def handle_auto_hw(client, duration, until):
    if duration or until:
        raise CommandException('auto mode does not allow duration or until time')
    client.set_hotwater_auto()

@cli.command()
@click.argument('state', callback=hw_mode_check)
@click.option('--duration', type=int, help='Duration of override in minutes')
@click.option('--until', callback=check_and_convert_hh_mm, help='Local time in HH:MM to override until')
def hotwater(state, duration, until):
    client = get_client()
    if state == 'auto':
        handle_auto_hw(client, duration, until)
        return
    states = { 
        'on' : client.set_hotwater_on, 
        'off': client.set_hotwater_off,
        }
    if not state in states:
        raise CommandException('illegal state specified - {}'.format(state))
    until = get_until_time(duration, until)
    states[state](until)


@cli.command()
@click.option('--no-flat/--flat', default=True, help='Output on single line')
def temps(no_flat):
    zone_temps = get_client().get_temperatures()
    format = '{} {} {}\n' if no_flat else '{}:{}/{} '
    output = [ ]
    for device in zone_temps:
        temp, setpoint = zone_temps[device]
        output.append(format.format(device, temp, setpoint))
    print ''.join(output)

if __name__ == '__main__':
    try:
        cli()
    except CommandException as e:
        print 'Error: {}'.format(str(e))
        sys.exit(1)
