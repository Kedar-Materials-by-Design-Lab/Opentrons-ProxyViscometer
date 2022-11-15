"""
OT-2 High-throughput Proxy Viscometer Protocol

Author: AMDM Group @ IMRE, A STAR
Date: July 2022
"""

from opentrons import protocol_api
import json

metadata = {'apiLevel': '2.10'}     # Opentrons Python API Version


def run(protocol: protocol_api.ProtocolContext):

    # falcon tube holder custom labware definition - json file generated using Opentrons' custom labware creator: https://labware.opentrons.com/create/
    # .stl file for 3d-printing this holder provided in the SI
    AMDM_12_50ml_falcon_tube_DEF_JSON = """{
    "ordering":[["A1","B1","C1"],["A2","B2","C2"],["A3","B3","C3"],["A4","B4","C4"]],
    "brand":{"brand":"AMDM","brandId":["AMDM"]},
    "metadata":{"displayName":"AMDM 12 50ml falcon tube","displayCategory":"reservoir","displayVolumeUnits":"µL","tags":[]},
    "dimensions":{"xDimension":127.76,"yDimension":85.47,"zDimension":119.36},
    "wells":{"A1":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":21,"y":70.97,"z":5.4},"B1":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":21,"y":43.61,"z":5.4},"C1":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":21,"y":15.25,"z":5.4},"A2":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":49.6,"y":70.97,"z":5.4},"B2":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":49.6,"y":43.61,"z":5.4},"C2":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":49.6,"y":15.25,"z":5.4},"A3":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":78.2,"y":70.97,"z":5.4},"B3":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":78.2,"y":43.61,"z":5.4},"C3":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":78.2,"y":15.25,"z":5.4},"A4":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":106.8,"y":70.97,"z":5.4},"B4":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":106.8,"y":43.61,"z":5.4},"C4":{"depth":116,"totalLiquidVolume":50000,"shape":"circular","diameter":27.44,"x":106.8,"y":15.25,"z":5.4}},
    "groups":[{"metadata":{"wellBottomShape":"v"},"wells":["A1","B1","C1","A2","B2","C2","A3","B3","C3","A4","B4","C4"]}],
    "parameters":{"format":"irregular",
    "quirks":[],
    "isTiprack":false,
    "isMagneticModuleCompatible":false,
    "loadName":"amdm_12_50ml_falcon_tube"},
    "namespace":"custom_beta",
    "version":1,
    "schemaVersion":2,
    "cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}"""

    AMDM_12_50ml_falcon_tube = json.loads(AMDM_12_50ml_falcon_tube_DEF_JSON)    # load the labware definition to this protocol

    # 2nd argument denotes position on the Opentrons plate
    reservoir = protocol.load_labware_from_definition(AMDM_12_50ml_falcon_tube, 1)  # custom labware
    plate = protocol.load_labware('corning_6_wellplate_16.8ml_flat', 2)             # Corning 6-well plate
    tiprack_1 = protocol.load_labware('opentrons_96_filtertiprack_1000ul', 7)       # Used Thermo Scientific 1000 uL wide bore tips
    p1000 = protocol.load_instrument('p1000_single', 'left', tip_racks=[tiprack_1])

    fr_arr            = [50]  # dispensed flowrate/uL/s
    samples_ran       = 0     # initialisation counter
    no_of_samples     = 2
    adepth            = 0    # initialisation - will account for what depth to aspirate from depending on past history of volume dispensed
    depth             = -80  # 80 mm from top corresponds to ~ 12.5 mL: fill the reservoir tubes to approx. 20 mL
    asptime           = 7.5  # protocol aspiration time fixed to 7.5 seconds
    disptime          = 5    # protocol dispense time fixed to 5 seconds
    well_touch_depth  = 0    # touch_tip height on dispense plate (Corning 6-well plate)

    # Location of stored liquids & destinations
    res_letter_list = ["A", "C"]
    well_letter_list = ["A", "B"]
                                                             
    while samples_ran < no_of_samples:
        i = 0
        # "dummy run" - systematic error correction of exterior excess weight
        if i == 0:
            p1000.pick_up_tip(tiprack_1["A" + str(samples_ran+1)])   # pick up pipette tip
            for e in range(3):  # triplicate measurements - pipette directed to same position, mass measurements in between to distinguish mass added each time
                # reservoir section
                p1000.move_to(reservoir[str(res_letter_list[samples_ran])+"1"].top(z=depth))    # move to the reservoir well, without aspirating
                protocol.delay(seconds=10)  # 10 second asp_delay

                # falcon tube touch tip
                for e in range(2):
                    p1000.touch_tip(radius=1, v_offset=-10)     # touch the pipette tip across the 4 opposite walls 10 mm into the falcon tube x2
                p1000.touch_tip(radius=1, v_offset=-1)          # touch tip @ 1 mm into the falcon tube
                p1000.touch_tip(radius=1.2, v_offset=0)         # touch tip @ the top of the falcon tube

                # plate touch tip
                p1000.move_to(plate[str(well_letter_list[samples_ran]) + "1"].top())    # send to destination position on Corning-6 well plate
                protocol.delay(seconds=5)   # 5 second dispense delay
                p1000.touch_tip(plate[str(well_letter_list[samples_ran]) + "1"], v_offset=well_touch_depth, speed=400)  # touch the pipette tip at the surface of the well plate
                p1000.move_to(reservoir[str(res_letter_list[samples_ran])+"1"].top())   # return the tip to the top of the well plate - during an actual run with fluid
                # fluid would be dispensed here
                protocol.pause("Time to measure.")  # take mass reading
                p1000.touch_tip(v_offset=-10)
            for e in range(10):     # 10 blowout cycles to dispose any residual material in the pipette tip
                p1000.blow_out(reservoir[str(res_letter_list[samples_ran])+"1"])

        # handling of viscous fluids
        for e in range(3):  # triplicate measurements
            # aspirate liquid
            depth -= adepth
            p1000.aspirate((fr_arr[i]*asptime), reservoir[str(res_letter_list[samples_ran])+"1"].top(z=depth), rate=100/274.7)  # aspirate 50 uL/s*7.5s = 375 uL

            # aspiration delay
            if (fr_arr[i]*asptime) <= 100:
                protocol.delay(seconds=10)
            elif 100 < (fr_arr[i]*asptime) <= 600:  # 375 uL falls within this category
                protocol.delay(seconds=20)          # 20 second aspiration delay
            else:
                protocol.delay(seconds=30)

            for e in range(2):  # touch tip x 2 @ -10 mm from top, x 1 @ -1 mm from top, x1 @ top
                p1000.touch_tip(radius=1, v_offset=-10)
            p1000.touch_tip(radius=1, v_offset=-1)
            p1000.touch_tip(radius=1.2, v_offset=0)
        
        # dispense liquid
            p1000.dispense((fr_arr[i]*disptime), plate[str(well_letter_list[samples_ran]) + "1"].top(10), rate=float(fr_arr[i]/274.7))
            p1000.touch_tip(v_offset=well_touch_depth, speed=400)
            p1000.move_to(reservoir[str(res_letter_list[samples_ran])+"4"].top())
            protocol.pause("Time to measure.")
        
        # getting rid of excess liquid
            p1000.dispense(1000, reservoir[str(res_letter_list[samples_ran])+"1"].top(), rate=100/274.7)
            protocol.delay(seconds=20)
            p1000.aspirate(400, reservoir[str(res_letter_list[samples_ran])+"1"].top(), rate=100/274.7)
            protocol.delay(seconds=10)
            p1000.dispense(400, reservoir[str(res_letter_list[samples_ran])+"1"].top(), rate=100/274.7)
            p1000.touch_tip(v_offset=-10)
            for e in range(10):
                p1000.blow_out(reservoir[str(res_letter_list[samples_ran])+"1"])
            
        # add 1mm of depth for every 10000/9ul aspirated from falcon tube
            tdisp = (fr_arr[i]*disptime)/ 1000.0
            adepth = tdisp * (9/5)  # 5ml is 9mm
        
        i += 1  # useful if you wish to test multiple flow rates
        
        if i == len(fr_arr):

            for e in range(3):

                #reservoir section
                p1000.move_to(reservoir[str(res_letter_list[samples_ran])+"1"].top(z=depth))
                protocol.delay(seconds=10)

                for e in range(2):
                    p1000.touch_tip(radius=1, v_offset=-10)
                p1000.touch_tip(radius=1, v_offset=-1)
                p1000.touch_tip(radius=1.2, v_offset=0)

                #plate touch tip
                p1000.move_to(plate[str(well_letter_list[samples_ran]) + "1"].top())
                protocol.delay(seconds=5)
                p1000.touch_tip(plate[str(well_letter_list[samples_ran]) + "1"], v_offset=well_touch_depth, speed=400)  # speed = 400mm/s
                p1000.move_to(reservoir[str(res_letter_list[samples_ran])+"1"].top())
                protocol.pause("Time to measure.")
                p1000.touch_tip(v_offset=-10)
            for e in range(10):
                p1000.blow_out(reservoir[str(res_letter_list[samples_ran])+"1"])
            p1000.drop_tip()
            
        samples_ran += 1
        depth = -80     