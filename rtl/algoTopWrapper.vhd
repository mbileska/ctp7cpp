library IEEE;
use IEEE.STD_LOGIC_1164.all;
use ieee.numeric_std.all;

use work.algo_pkg.all;

entity algo_top_wrapper is
  port (
    ap_clk   : in  std_logic;
    ap_rst   : in  std_logic;
    ap_start : in  std_logic;
    ap_done  : out std_logic;
    ap_idle  : out std_logic;
    ap_ready : out std_logic;

    -- Input Links 
    link_in_master : in  LinkMasterArrType(35 downto 0);
    link_in_slave  : out LinkSlaveArrType(35 downto 0);

    -- Output Links 
    link_out_master : out LinkMasterArrType(1 downto 0);
    link_out_slave  : in  LinkSlaveArrType(1 downto 0)
    );
    
    attribute dont_touch : string;
    attribute dont_touch of algo_top_wrapper: entity is "true|yes";

end algo_top_wrapper;

architecture rtl of algo_top_wrapper is
  
  type t_cyc_4_arr is array(integer range <>) of integer range 0 to 3;
  type t_slv_128_arr is array(integer range <>) of std_logic_vector(127 downto 0);
  

  signal ap_rst_d1 : std_logic:='0';
  signal ap_rst_d2 : std_logic:='0';
  signal ap_rst_d3 : std_logic:='0';
  signal ap_rst_d4 : std_logic:='0';
  signal ap_rst_d5 : std_logic:='0';

  signal ap_clk_unp   : std_logic;
  signal ap_rst_unp   : std_logic;
  signal ap_start_unp : std_logic;
  signal ap_done_unp  : std_logic;
  signal ap_idle_unp  : std_logic;
  signal ap_ready_unp : std_logic;

 
  
  signal link_in      : t_slv_128_arr(35 downto 0);
  signal link_out     : t_slv_128_arr(1 downto 0);
  
  signal link_in_reg  : t_slv_128_arr(35 downto 0);
  signal link_out_reg : t_slv_128_arr(1 downto 0);

  signal link_out_ap_vld : std_logic_vector(1 downto 0);
  signal link_out_ap_vld_latched : std_logic_vector(1 downto 0);

  signal in_cyc  : t_cyc_4_arr(35 downto 0);
  signal out_cyc : t_cyc_4_arr(1 downto 0);

begin

  ap_done <= ap_done_unp;
  
  process(ap_clk) is
  begin
       if rising_edge(ap_clk) then
         ap_rst_d1 <= ap_rst;
         ap_rst_d2 <= ap_rst_d1;
         ap_rst_d3 <= ap_rst_d2;
         ap_rst_d4 <= ap_rst_d3;
         ap_rst_d5 <= ap_rst_d4;
     end if;
  end process;
  
  gen_4cyc_input : for idx in 0 to 35 generate
    process(ap_clk) is
    begin
      if rising_edge(ap_clk) then
      
        if (ap_rst_d1 = '1') then
          in_cyc(idx) <= 0;
        else
          in_cyc(idx) <= in_cyc(idx) + 1;
          if (in_cyc(idx) = 3) then
            in_cyc(idx) <= 0;
          end if;
        end if;
        
       if (in_cyc(idx) = 0) then 
            link_in(idx)(31 downto 0)    <= link_in_master(idx).tdata; 
        end if;
        
        if (in_cyc(idx) = 1) then 
            link_in(idx)(63 downto 32)  <= link_in_master(idx).tdata; 
        end if;
        
        if (in_cyc(idx) = 2) then 
            link_in(idx)(95 downto 64)  <= link_in_master(idx).tdata; 
        end if;
        
        if (in_cyc(idx) = 3) then 
            link_in_reg(idx)(31 downto 0) <= link_in(idx)(31 downto 0);
            link_in_reg(idx)(63 downto 32) <= link_in(idx)(63 downto 32);
            link_in_reg(idx)(95 downto 64) <= link_in(idx)(95 downto 64);
            link_in_reg(idx)(127 downto 96) <= link_in_master(idx).tdata; 
        end if;

      
      
      end if;
    end process; 
  end generate;
  
  
  gen_4cyc : for idx in 0 to 1 generate
    process(ap_clk) is
    begin
      if rising_edge(ap_clk) then

        if (link_out_ap_vld(idx) = '1') then
          link_out_reg(idx) <= link_out(idx);
        end if;
        
        if (ap_rst = '1') then
          link_out_ap_vld_latched(idx) <= '0';
        elsif (link_out_ap_vld(idx) = '1') then
          link_out_ap_vld_latched(idx) <= '1';
        end if;

        if (link_out_ap_vld_latched(idx) = '0') then
          out_cyc(idx)                <= 0;
          link_out_master(idx).tvalid <= '0';
        else
          link_out_master(idx).tvalid <= '1';
          out_cyc(idx)                <= out_cyc(idx) + 1;
          if (out_cyc(idx) = 3) then
            out_cyc(idx) <= 0;
          end if;
        end if;

       

        if (out_cyc(idx) = 0) then link_out_master(idx).tdata <= link_out_reg(idx)(31 downto 0); end if;
        if (out_cyc(idx) = 1) then link_out_master(idx).tdata <= link_out_reg(idx)(63 downto 32); end if;
        if (out_cyc(idx) = 2) then link_out_master(idx).tdata <= link_out_reg(idx)(95 downto 64); end if;
        if (out_cyc(idx) = 3) then link_out_master(idx).tdata <= link_out_reg(idx)(127 downto 96); end if;

      end if;
    end process;
  end generate;

  ap_clk_unp   <= ap_clk;
  ap_rst_unp   <= ap_rst;
  ap_start_unp <= not ap_rst_d5;
  ap_idle      <= ap_idle_unp;
  ap_ready     <= ap_ready_unp;
  
  i_algo_unpacked:algo_unpacked
 
    port map (
      ap_clk   => ap_clk_unp,
      ap_rst   => ap_rst_unp,
      ap_start => ap_start_unp,
      ap_done  => ap_done_unp,
      ap_idle  => ap_idle_unp,
      ap_ready => ap_ready_unp,

      link_in_0_V  => link_in_reg(0),
      link_in_1_V  => link_in_reg(1),
      link_in_2_V  => link_in_reg(2),
      link_in_3_V  => link_in_reg(3),
      link_in_4_V  => link_in_reg(4),
      link_in_5_V  => link_in_reg(5),
      link_in_6_V  => link_in_reg(6),
      link_in_7_V  => link_in_reg(7),
      link_in_8_V  => link_in_reg(8),
      link_in_9_V  => link_in_reg(9),
      link_in_10_V => link_in_reg(10),
      link_in_11_V => link_in_reg(11),
      link_in_12_V => link_in_reg(12),
      link_in_13_V => link_in_reg(13),
      link_in_14_V => link_in_reg(14),
      link_in_15_V => link_in_reg(15),
      link_in_16_V => link_in_reg(16),
      link_in_17_V => link_in_reg(17),
      link_in_18_V => link_in_reg(18),
      link_in_19_V => link_in_reg(19),
      link_in_20_V => link_in_reg(20),
      link_in_21_V => link_in_reg(21),
      link_in_22_V => link_in_reg(22),
      link_in_23_V => link_in_reg(23),
      link_in_24_V => link_in_reg(24),
      link_in_25_V => link_in_reg(25),
      link_in_26_V => link_in_reg(26),
      link_in_27_V => link_in_reg(27),
      link_in_28_V => link_in_reg(28),
      link_in_29_V => link_in_reg(29),
      link_in_30_V => link_in_reg(30),
      link_in_31_V => link_in_reg(31),
      link_in_32_V => link_in_reg(32),
      link_in_33_V => link_in_reg(33),
      link_in_34_V => link_in_reg(34),
      link_in_35_V => link_in_reg(35),
      
      link_out_0_V  => link_out(0),
      link_out_1_V  => link_out(1),
      
      link_out_0_V_ap_vld  => link_out_ap_vld(0),
      link_out_1_V_ap_vld  => link_out_ap_vld(1)
      
      );

end architecture rtl;
