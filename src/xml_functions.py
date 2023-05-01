"""Main functions for ephys processing"""
from typing import Dict, Any

import pandas as pd
import xml.etree.ElementTree as et


def get_recording_info(file_name):
    """
    Retrieve recording information for the TIFF, CSV, and XML files.
    """
    tree = et.parse(file_name)
    root = tree.getroot()
    version = root.attrib['version']
    date_time = root.attrib['date']
    patch_data_file = root.find('.//VoltageRecording').attrib['dataFile']
    configuration_file = root.find('.//VoltageRecording').attrib['configurationFile']
    voltage_output = root.find('.//VoltageOutput').attrib['filename']
    acquisition_type = root.find('.//Sequence').attrib['type']

    return {
        "PVScan version": version,
        "Date and time": date_time,
        "Patch data file": patch_data_file,
        "Configuration file": configuration_file,
        "VoltageOutput file": voltage_output,
        "Acquisition type": acquisition_type
    }


def import_ephys(file_name):
    recording = pd.read_table(file_name, sep=r',', skipinitialspace=True)
    print(recording.head())
    return recording


def parse_voltage_recording(voltage_recording_xml_file):
    """This is for the VoltageRecording XML file."""
    tree = et.parse(voltage_recording_xml_file)
    root = tree.getroot()
    signal_list = []
    for element in root:
        data_dict = _element_to_dict(element)
        if data_dict:
            signal_list.append(data_dict)
    return signal_list


def parse_voltage_recording_xml(file_name):
    tree = et.parse(xml_file_name)
    root = tree.getroot()
    # create a dictionary of dictionaries for each VRecSignal node
    signals_dict = {}
    rec_name = []
    date_name = []
    for signal in root.findall(".//VRecSignal"):
        name = signal.find("Name").text
        unit_name = signal.find("Unit/UnitName").text
        unit_multiplier = float(signal.find("Unit/Multiplier").text)
        unit_divisor = float(signal.find("Unit/Divisor").text)
        try:
            unit_device = signal.find("Unit/PatchClampDevice").text
        except:
            unit_device = "None"
        try:
            unit_channel = signal.find("Unit/PatchClampChannel").text
        except:
            unit_channel = "None"

        signal_type = signal.find("Type").text
        signal_gain = float(signal.find("Gain").text)
        signal_channel_num = int(signal.find("Channel").text)
        signal_enabled = signal.find("Enabled").text

        signals_dict[name] = {
            "unit_name": unit_name,
            "unit_multiplier": unit_multiplier,
            "unit_divisor": unit_divisor,
            "signal_type": signal_type,
            "signal_enabled": signal_enabled,
            "signal_gain": signal_gain,
            "signal_channel_number": signal_channel_num,
            "unit_device": unit_device,
            "unit_channel": unit_channel
        }

    acquisition_time_ms = root.find("Experiment/AcquisitionTime").text
    sampling_rate = root.find("Experiment/Rate").text
    recording_name = root.find("DataFile").text
    recording_datetime = root.find("DateTime").text

    return


def _element_to_dict(element):
    result = {}
    for child in element:
        if len(child) == 0:
            result[child.tag] = child.text
        else:
            result[child.tag] = _element_to_dict(child)
    return result if len(result) > 0 else None


def parse_voltage_output_xml(xml_file):
    tree = et.parse(xml_file)
    root = tree.getroot()
    channel_list = []
    for element in root:
        data_dict = _element_to_dict(element)
        if data_dict:
            channel_list.append(data_dict)
    return channel_list


def enumerate_channels(channel_list):
    """
    This is for the VoltageOutput XML file.
    Separate each dictionary entry in a list into a new variable called channel_x where x is the index in the list.
    :param channel_list: a list of dictionaries
    :return: a dictionary with keys channel_1, channel_2, channel_3, etc.
    """
    channel_dict = {}
    for i, channel in enumerate(channel_list):
        name = channel['Name']
        channel_dict['channel_{}'.format(i+1)] = channel
    return channel_dict


def find_waveform_components(channel_dict):
    """
    This is for the VoltageOutput XML file.
    :param channel_dict:
    :return:
    """
    waveform_dict = {}
    for dict_name, data in channel_dict.items():
        components = []
        for key, value in data.items():
            if isinstance(value, dict) and key.startswith('WaveformComponent_'):
                components.append(key)
        waveform_dict[dict_name] = components
    return waveform_dict

#%%
