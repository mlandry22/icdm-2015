require(data.table)
val = read.csv("val_predictions.csv")
val_newvars <- data.table(val)[,list( count_cookie=.N, min_pred_val=min(prediction), max_pred_val=max(prediction), mean_pred_val=mean(prediction), num_greater_point9=sum(prediction>0.9)), by=device_id]
new_val <- merge(x=val, y=val_newvars, by="device_id", all.x=T)
new_val["diff_from_max"] = new_val$max_pred_val - new_val$prediction
write.csv(new_val, "mod_val_preds.csv", quote=F, row.names=F)

test = read.csv("test_predictions.csv")
test_newvars <- data.table(test)[,list( count_cookie=.N, min_pred_val=min(prediction), max_pred_val=max(prediction), mean_pred_val=mean(prediction), num_greater_point9=sum(prediction>0.9)), by=device_id]
new_test <- merge(x=test, y=test_newvars, by="device_id", all.x=T)
new_test["diff_from_max"] = new_test$max_pred_val - new_test$prediction
write.csv(new_test, "mod_test_preds.csv", quote=F, row.names=F)
