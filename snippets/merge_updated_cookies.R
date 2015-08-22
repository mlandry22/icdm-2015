## This is an example script that you can easily use to:
##   merge two files together based on cookie, including a file that may be incomplete
##   use the drawbridge IDs to supplement additional cookies
##   merge cookies per device
##   output a CSV
##

library(data.table)
a<-fread("id_10_fixes.csv")
b<-fread("../../../Data/cookie_all_basic.csv")
a<-merge(a,b[,1:2,with=F],by="cookie_id",all.x=TRUE)
a$drawbridge_handle[a$drawbridge_handle=="-1"]<-"-999"	## to avoid matching all the -1s in cookies
a<-merge(a[,c(2,3),with=F],b[,1:2,with=F],by="drawbridge_handle",allow.cartesian=T)
a <- a[, .(cookie_id=paste(cookie_id, collapse=' ')), device_id]
srk<-fread("SRKsub21.csv")
s2<-merge(srk,a,by="device_id",all.x=TRUE)
s2[,cookie_id:=ifelse(is.na(cookie_id.y),cookie_id.x,cookie_id.y)]
write.csv(s2[,.(device_id,cookie_id)],"sub21b.csv",row.names=F,quote=F)
