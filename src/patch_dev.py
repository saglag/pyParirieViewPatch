# TODO: Initially built on a PVScan version 5.7.64.300, obtain versions to check compatibility
"""Code here creates the class PATCH for patch clamp recordings generated from Bruker PrarieView. The information
required is:
    • CSV file of the recording. This contains the actual recorded input and output data.
    • XML file of the VoltageOutput (Usually titled _Cycle00001_VoltageOutput_001.xml). This contains information
      relating to the various Outputs that are configured for the recording.
    • XML file of the VoltageRecording (Usually titled _Cycle00001_VoltageRecording_001.xml). This contains information
      relating to the settings of the amplifier as well as number of samples and date information.

This file is LIMITED TO THE MANAGEMENT OF XML AND CSV information for patch-clamp recordings. Other types of
recordings are not currently supported.

Inspiration for this class comes from pyABF.
"""
import os
import numpy as np
import pathlib
from typing import Union, List, Tuple
import pandas as pd
import xml_functions as xml


class PATCH_dev:
    """
    The PATCH class provides access to the metadata (XML) and signal data (CSV) of the recording.
    """

    def __init__(self,
                 patch_csv_file_path: Union[str, pathlib.Path],
                 voltage_output_xml_path: Union[str, pathlib.Path],
                 voltage_recording_xml_path: Union[str, pathlib.Path],
                 base_xml: Union[str, pathlib.Path],
                 load_data: bool = True):
        """
        Load XML and CSV data from their respective files.
        ### Parameters
        1. patch_csv_file_path -- Path to the CSV file.
        2. voltage_output_xml_path -- Path to the VoltageOutput XML file.
        3. voltage_recording_xml_path -- Path to the VoltageRecording XML file.
        4. base_xml -- Path to the base XML file.
        5. load_data -- Load the CSV and XML data files.
        """

        if isinstance(patch_csv_file_path, pathlib.Path):
            patch_csv_file_path = str(patch_csv_file_path)

        if patch_csv_file_path.lower() and not patch_csv_file_path.endswith('.csv'):
            raise Exception("Patch file must be a CSV!")

        if os.path.isdir(patch_csv_file_path):
            raise Exception("CSV path must be a path to a FILE not a FOLDER.")

        self._preLoadData = load_data

        self.patch_csv_file_path = os.path.abspath(patch_csv_file_path)
        self.patch_csv_folder_path = os.path.dirname(self.patch_csv_file_path)

        self.patch_voltage_output_xml_path = os.path.abspath(voltage_output_xml_path)
        self.patch_voltage_output_folder_path = os.path.dirname(self.patch_voltage_output_xml_path)

        self.patch_voltage_recording_xml_path = os.path.abspath(voltage_recording_xml_path)
        self.patch_voltage_recording_folder_path = os.path.dirname(self.voltage_recording_xml_path)

        if not os.path.exists(self.patch_csv_file_path):
            raise ValueError("CSV file does not exist: %s" % self.patch_csv_file_path)
        self.patchID = os.path.splitext(os.path.basename(self.patch_csv_file_path))[0]

        if not os.path.exists(self.patch_voltage_output_xml_path):
            raise ValueError("Voltage Output XML file does not exist: %s" % self.patch_voltage_output_xml_path)
        self.voltageOutputID = os.path.splitext(os.path.basename(self.patch_voltage_output_xml_path))[0]

        if not os.path.exists(self.patch_voltage_output_xml_path):
            raise ValueError("Voltage Recording XML file does not exist: %s" % self.patch_voltage_recording_xml_path)
        self.voltageRecordingID = os.path.splitext(os.path.basename(self.patch_voltage_recording_xml_path))[0]

        if isinstance(voltage_output_xml_path, pathlib.Path):
            voltage_output_xml_path = str(voltage_output_xml_path)

        if voltage_output_xml_path.lower and not voltage_output_xml_path.endswith('.xml'):
            raise Exception("Voltage Output file must be an XML!")

        if os.path.isdir(voltage_output_xml_path):
            raise Exception("Voltage Output XML path must be a path to a FILE not a FOLDER!")

        if isinstance(voltage_recording_xml_path, pathlib.Path):
            voltage_recording_xml_path = str(voltage_recording_xml_path)

        if voltage_recording_xml_path.lower and not voltage_recording_xml_path.endswith('.xml'):
            raise Exception("Voltage Recording file must be an XML!")

        if os.path.isdir(voltage_recording_xml_path):
            raise Exception("Voltage Recording XML path must be a path to a FILE not a FOLDER!")

        # TODO: add base xml info to class to get PVScan version and any application notes.
        # TODO: Alternative: import base XML which contains the names for the CSV and other XML file names.
        if load_data:

            # Load the recorded data
            self.recording = pd.read_table(self.patch_csv_file_path, sep=r',', skipinitialspace=True)
            column_names = []
            for col in self.recording.columns:
                column_names.append(col)
            # TODO: Correct data scale using unit divisor and convert ms to s

            # TODO: Update load_data to contain all the useful XML data
            # VoltageOutput contains protocol/waveform info
            self.protocol = ""
            channel_list = xml.parse_voltage_output_xml(voltage_output_xml_path)
            self.protocol = xml.enumerate_channels(channel_list)
            # VoltageRecording contains DAQ signal info, and some experiment info
            self.DAQ_info = ""
            self.recording_datetime = ""

            self.DAQ = xml.parse_voltage_recording_xml(voltage_recording_xml_path)
            self.waveforms = xml.find_waveform_components(self.DAQ)

            # TODO: return only channels that are enabled
    def __str__(self):
        """
        Return a string describing basic properties of the loaded patch recording.
        """
        txt = """
        PVScan (vVERSN)
        with CHNM channels (CHUNITS),
        sampled at RATEKHZ kHz,
        having no notes,
        with a total length of LENMIN minutes.
        """.strip().replace("\n", "  ")
        while " " in text:
            txt = txt.replace("  ", " ")