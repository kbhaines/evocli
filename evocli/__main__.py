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

def calculate_offset_time(minutes):
    if not minutes:
        return None
    return datetime.now() + timedelta(0, minutes*60)

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
    
@click.group()
def cli():
    pass

def temperature_range_check(ctx, param, value):
    if value < 0.0 or value > 30.0:
        raise click.BadParameter('temperature must be 0 - 30 degrees')
    return value

@cli.command()
@click.argument('zone')
@click.argument('temperature', callback=temperature_range_check, type=float)
@click.option('--duration', type=int, help='Duration of override in minutes')
def zone(zone, temperature, duration):
    try:
        until = calculate_offset_time(duration)
        get_client().set_zone_temperature(zone, temperature, until)
    except KeyError:
        raise CommandException('Zone {} was not found'.format(zone))


def handle_auto_hw(client, duration):
    if duration:
        raise CommandException('auto mode does not allow duration')
    client.set_hotwater_auto()

def hw_mode_check(ctx, param, value):
    if not value in ['on', 'off', 'auto']:
        raise CommandException('Invalid mode')

@cli.command()
@click.argument('state', callback=hw_mode_check)
@click.option('--duration', type=int, help='Duration of override in minutes')
def hotwater(state, duration):
    client = get_client()
    if state == 'auto':
        handle_auto_hw(client, duration)
        return
    states = { 
        'on' : client.set_hotwater_on, 
        'off': client.set_hotwater_off,
        }
    if not state in states:
        raise CommandException('illegal state specified - {}'.format(state))
    if duration and (duration < 10 or duration > 24 * 60):
        raise CommandException('duration must be 10 to 1440 minutes')
    until = calculate_offset_time(duration)
    states[state](until)

@cli.command()
def temps():
    zone_temps = get_client().get_temperatures()
    for device in zone_temps:
        temp, setpoint = zone_temps[device]
        print '{} {} {}'.format(device, temp, setpoint)

def load_config_file():
    config_file = os.path.expanduser('~/.evoc')
    if not os.path.isfile(config_file):
        raise CommandException('Config file ({}) not found'.format(config_file))
    return yaml.load(open(config_file))

def get_client():
    config = load_config_file()
    #return DummyClient()
    user = config['username']
    password = config['password']
    return clients.EvohomeControlClient(user, password)

if __name__ == '__main__':
    try:
        cli()
    except CommandException as e:
        print 'Error: {}'.format(str(e))
        sys.exit(1)
