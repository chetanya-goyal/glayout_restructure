* include from .../sky130A/libs.tech/ngspice/sky130.lib.spice
.lib '@model_file' @model_corner
* include the LDO spice netlist
.include 'ldo_sim.spice'


xi1 clk cmp_out ctrl_out[0] ctrl_out[1] ctrl_out[2] ctrl_out[3]
+ ctrl_out[4] ctrl_out[5] ctrl_out[6] ctrl_out[7] ctrl_out[8] mode_sel[0] mode_sel[1]
+ reset std_ctrl_in std_pt_in_cnt[0] std_pt_in_cnt[1] std_pt_in_cnt[2] std_pt_in_cnt[3]
+ std_pt_in_cnt[4] std_pt_in_cnt[5] std_pt_in_cnt[6] std_pt_in_cnt[7] std_pt_in_cnt[8]
+ trim1 trim10 trim2 trim3 trim4 trim5 trim6 trim7 trim8 trim9 VDD VSS VREF VREG @design_nickname


*Controls
V0 VSS 0 dc 0
V1 VDD VSS pwl 0 0 2n 0 2.0001n 3.3
V2 VREF VSS pwl 0 0 2n 0 2.0001n 1.8
V3 clk  VSS pulse 0 3.3 0 1p 1p 0.5u 1u
V4 reset VSS pwl 0 3.3 5n 0
V5 mode_sel[0] VSS 3.3
V6 mode_sel[1] VSS 3.3
vctrl std_ctrl_in 0 dc 0
vstd0 std_pt_in_cnt[0] 0 dc 0
vstd1 std_pt_in_cnt[1] 0 dc 0
vstd2 std_pt_in_cnt[2] 0 dc 0
vstd3 std_pt_in_cnt[3] 0 dc 0
vstd4 std_pt_in_cnt[4] 0 dc 0
vstd5 std_pt_in_cnt[5] 0 dc 0
vstd6 std_pt_in_cnt[6] 0 dc 0
vstd7 std_pt_in_cnt[7] 0 dc 0
vstd8 std_pt_in_cnt[8] 0 dc 0
R1 VREG VSS 3.6k
C1 VREG VSS 100n


*.options savecurrents
.options rshunt=1e11
.ic v(VREG) = 0 v(clk) =0 v(reset)=3.3
*Analysis
.temp 25
.tran 50u 300u uic

.op
.meas TRAN id find I(R1) AT=300u
.meas TRAN vout find V(VREG) AT=300u
.meas TRAN vrs find V(reset) AT=300u
.meas TRAN vr find V(VREF) AT=300u

.PROBE v(clk) v(reset) v(VREF) v(VREG) v(cmp_out) I(R1)
.control
run
.endc
.GLOBAL VDD
.GLOBAL VSS
.end
