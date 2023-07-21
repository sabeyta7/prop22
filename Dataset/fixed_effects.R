# Loading required package: ggplot2, dplyr, tidyr, stan, brms, rstan, shiny, shinyda
library(ggplot2)
library(dplyr)
library(tidyr)
library(brms)
library(rstan)
library(lubridate)
library(bayesplot)
library(plm)
library(car)
library(caret)
library(lmtest)
library(haven)

# Get the current working directory
current_dir <- getwd()

# Print the current working directory
print(current_dir)


# Loading in data
data <- read.csv(".Project_Data.csv")


# Convert threshold times to date objects
threshold_time_1 <- as.Date('2020-01-01')
threshold_time_2 <- as.Date('2020-03-01')
threshold_time_3 <- as.Date('2021-01-01')
threshold_time_4 <- as.Date('2022-12-01')

# Assuming your data frame is named data
# Making the experimental conditions columns
data$california <- ifelse(data$state == 'California', 1, 0)
data$washington <- ifelse(data$state == 'Washington', 1, 0)

# Making the critical date columns
data$ab_5 <- ifelse(data$date >= threshold_time_1, 1, 0)
data$pandemic <- ifelse(data$date >= threshold_time_2, 1, 0)
data$prop_22 <- ifelse(data$date >= threshold_time_3, 1, 0)
data$washington_bill <- ifelse(data$date >= threshold_time_4, 1, 0)


# Create a variable for log of population ind_participant and medicaid_chip_enrollment
data$log_popest <- log(data$popest)

# Standardize the ind_participant and medicaid_chip_enrollment columns 
data$ind_participant_std <- (data$ind_participant - mean(data$ind_participant)) / sd(data$ind_participant)
data$medicaid_chip_enrollment_std <- (data$medicaid_chip_enrollment - mean(data$medicaid_chip_enrollment)) / sd(data$medicaid_chip_enrollment)


# Convert the 'date' column to a proper date format
data$date <- ymd(data$date)

# Calculate the number of months elapsed since January 2021 (prop_22)
data$month_count <- as.numeric(interval("2021-01-01", data$date) / months(1))

# Round the month_count to integers (optional, if you want integer values)
data$month_count <- round(data$month_count)


# Two way fixed effects model


# Create the pdata.frame
pdata <- pdata.frame(data, index = c("state", "month_count"))

# Check for duplicate combinations of state and year
duplicate_combinations <- table(index(pdata), useNA = "ifany")

# Assuming 'pdata' contains the panel data with relevant columns and the model with an intercept is already fitted
lf_model <- plm(percent_labor_force ~  california + prop_22 + california:prop_22 + log_popest + pandemic  + 1,
                            data = pdata,
                            model = "within",
                            index = c("state", "month_count"),
                            effect = "twoways")

coeftest(lf_model, vcov = vcovHC, type = "HC1")

# Assuming 'pdata' contains the panel data with relevant columns and the model with an intercept is already fitted
medic_model <- plm(medicaid_chip_enrollment_std ~  california + prop_22 + california:prop_22 + log_popest + pandemic   + 1,
                            data = pdata,
                            model = "within",
                            index = c("state", "month_count"),
                            effect = "twoways")

coeftest(medic_model, vcov = vcovHC, type = "HC1")

snap_model <- plm(ind_participant_std ~  california + prop_22 + california:prop_22 + log_popest + pandemic + 1,
                            data = pdata,
                            model = "within",
                            index = c("state", "month_count"),
                            effect = "twoways")

coeftest(snap_model, vcov = vcovHC, type = "HC1")

unemp_model <- plm(rate_unemployed ~  california + prop_22 + california:prop_22 + log_popest + pandemic + 1,
                            data = pdata,
                            model = "within",
                            index = c("state", "month_count"),
                            effect = "twoways")

coeftest(unemp_model, vcov = vcovHC, type = "HC1")


















































# Standardizing the ind_participant and medicaid_chip_enrollment columns by dividing by popest and multiplying by 100
data$ind_participant_100 <- data$ind_participant / data$popest * 100
data$medicaid_chip_enrollment_100 <- data$medicaid_chip_enrollment / data$popest * 100

# Make sure these variables are floats by converting to character and then to numeric
data$ind_participant_100 <- as.numeric(as.character(data$ind_participant_100))
data$medicaid_chip_enrollment_100 <- as.numeric(as.character(data$medicaid_chip_enrollment_100))