library(DBI)
# data without connected = false
con = dbConnect(RSQLite::SQLite(), dbname="data.db")
data3 = dbGetQuery( con,'select * from data2 where connected=1' )
head(data3)

# Model1: Normalised cdn against p2p to check linear relation
model1 = lm(cdnnorm ~ p2pnorm, data = data3)
summary(model1)
plot(residuals(model1))

# Model2 = p2p against browser and isp with dependence
model2 = lm(p2pnorm ~ browser * isp, data = data3)
summary(model2)

# Model3 = p2p against browser and isp independent
model3 = lm(p2pnorm ~ browser + isp, data = data3)
summary(model2)

# Comparison of model2 and model3
anova(model2,model3)
