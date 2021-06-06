### Number of confusing doublets
data <- read.csv("./results/results-number-confusing-doublets.csv")
rownames(data) <- data$substitution
data <- data[!(rownames(data) %in% c("G", "N", "x")), ] #deletion of phonemes borrowed from other languages

# For each liaison consonant, we run a Wilcoxon  test
# We compare the numbers obtained with the substitutions = realFre
# to the number obtained for the real French = altFre

## function
#liaisonCons is a String
#liaisonCons -> WilcoxTest
#Performs a One sample Wilcoxon Test with a given liaison consonant
wilcoxTestNumber<- function(liaisonCons) {
  realFre <- data[liaisonCons,liaisonCons]
  altFre <- subset(data, data$substitution != liaisonCons)
  altFre <- altFre[, liaisonCons]
  wilcoxTest <-  wilcox.test(altFre, mu = realFre, alternative = "greater") 
  return(wilcoxTest)  
}

#tests
gTest <- wilcoxTestNumber("g")
nTest <- wilcoxTestNumber("n")
pTest <- wilcoxTestNumber("p")
RTest <- wilcoxTestNumber("R")
tTest <- wilcoxTestNumber("t")
zTest <- wilcoxTestNumber("z")

#showing results
gTest
nTest
pTest
RTest
tTest
zTest
