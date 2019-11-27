* Name: Zhenxing Xie
* PID: A53237274

/* Preliminary stuff */

clear

/* Part 1 */

use "E:\stata code\haidian-panel.dta", clear
save haidian-panel-test.dta,replace

bysort community: gen id = 1 if _n==1
replace id = sum(id)
replace id = . if missing(id)

tsset id year
xtset id year

gen logprice = log(transactionprice)

gen logtolsqft = log(totaltransactedsquarefootage)

gen logavtsqft = log(avgtransactedsquarefootage)

gen logamount = log(totaltransactionamount)

gen logvolume = log(totalnumberofhousessold)

gen logdistsp = log(DISTANCE to SP)

gen logdistzgc = log(Distance to ZGC)

/* Part 2 */

set matsize 11000

/* FE */

xtreg logprice c.logdistsp#i.year c.logdistzgc#i.year logtolsqft logvolume i.year, i(id) fe vce(cluster id)

xtreg logprice c.logdistsp#i.year c.logdistzgc#i.year logavtsqft logvolume i.year, i(id) fe vce(cluster id)

/* RE */

xtreg logprice c.logdistsp#i.year c.logdistzgc#i.year logtolsqft logvolume i.year, i(id) re vce(cluster id)

xtreg logprice c.logdistsp#i.year c.logdistzgc#i.year logavtsqft logvolume i.year, i(id) re vce(cluster id)

xtreg logprice logdistsp logdistzgc logtolsqft logvolume i.year, i(id) re vce(cluster id)



/* Pooled OLS */

reg logprice c.logdistsp#i.year c.logdistzgc#i.year logtolsqft logvolume i.id i.year,robust

reg logprice c.logdistsp#i.year c.logdistzgc#i.year logavtsqft logvolume i.id i.year,robust

/* 
encode transactionprice, gen(price) 
encode totaltransactedsquarefootage, gen(tolsqft)
encode avgtransactedsquarefootage, gen(avgsqft)
encode totaltransactionamount, gen(tolamount)
encode totalnumberofhousessold, gen(tolvolume)
 */


