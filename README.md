# Opentrons High-Throughput Proxy Viscometer

Supplementary Information (SI) for our paper titled **_Automated Pipetting Robot for Proxy High-Throughput Viscometry of Newtonian Fluids_**

`OT-2_ProxyViscometerProtocol.py` is the main file required to reproduce the protocol illustrated in the paper. It needs to be uploaded via the Opentrons App. 

To run the experiment, as shown in the paper, one needs to use the `falcon_tube_holder.stl` file (in the ‘Labware_Files’ directory) to 3d-print the MTP-sized labware holder for the 50 mL Falcon® centrifuge tubes (VWR). The custom labware definition, required for the Opentrons robot to understand the utilised geometry, has already been included as part of the main Python protocol file. No additional files are required. 

Additionally, the Autodesk Fusion (Computer-Aided Design) file for the customised 1 mL pipette tip shown in the paper has been provided as `CustomDesignedTip_1000uL.f3d`. This is an initial example of the many possibilities via which the design of the pipette tips could be modified to alter the range of viscosities measurable with the presented methodology. 
