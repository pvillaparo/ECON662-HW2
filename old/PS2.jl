#Problem Set 2
#Name : Paola Villa
################################################
#Set up the environment
    ################################################

    using Statistics

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
#Simulated Data
#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    const DATA_PATH = "ddc_pset.csv" data = read_data(DATA_PATH)

#key complication vs.the classic Rust(1987) model is that $RC_t$ is stochastic and continuous,
 #so Harold Jr.must integrate over future $RC$ values when computing expected value functions.

 #-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Method A : Rust NXP
#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

