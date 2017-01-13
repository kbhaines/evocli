#!/usr/bin/env python
#
from datetime import datetime
from datetime import timedelta
from evohomeclient2 import EvohomeClient
from evocli.dummyclient import DummyClient

import sys

import click

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
    hotwater = client._get_single_heating_system().hotwater
    hotwater.set_dhw_auto()
    
@click.group()
@click.option('--username', help='username')
@click.option('--password', help='password')
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
        client = get_client()._get_single_heating_system()
        until = calculate_offset_time(duration)
        client.zones[zone].set_temperature(temperature, until)
    except KeyError:
        raise CommandException('Zone {} was not found'.format(zone))


@cli.command()
@click.argument('state')
@click.option('--duration', type=int, help='Duration of override in minutes')
def hotwater(state, duration):
    states = { 
        'on' : hotwater_on_off, 
        'off': hotwater_on_off,
        'auto': hotwater_auto 
        }
    if state == 'auto' and duration:
        raise CommandException('auto mode does not allow duration')
    if not state in states:
        raise CommandException('illegal state specified - {}'.format(state))
    if duration and (duration < 10 or duration > 24 * 60):
        raise CommandException('duration must be 10 to 1440 minutes')

    client = get_client()
    states[state](client, state, duration)

@cli.command()
def temps():
    client = get_client()
    temperatures = client._get_single_heating_system().temperatures()
    for device in temperatures:
        name = 'WATER' if device['thermostat'] == 'DOMESTIC_HOT_WATER' else device['name']
        print '{} {} {}'.format(name, device['temp'], device['setpoint'])

def get_client(user, password):
    #return DummyClient()
    return EvohomeClient(user, password)

if __name__ == '__main__':
    try:
        cli()
    except CommandException as e:
        print 'Error: {}'.format(str(e))
        sys.exit(1)
