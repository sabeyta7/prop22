rm(list = ls())                               #Clean the Global Environment
if (is.null(dev.list()) == FALSE) dev.off()   #Clean Plots
cat("\014")

pacman::p_load(readxl, ggplot2, tidyverse, lubridate)

df <- read_csv("indeed_for_R.csv")
df_full <- read_csv("indeed_for_R_with_all_sentiments.csv")
df_full$date <- as.Date(df_full$datetime, "%Y-%m-%d")


# Replace zeros with NAs 
df <- df %>%
  mutate_at(vars(job_work_and_life_balance_rating, 
                 compensation_and_benefits_rating, 
                 job_security_and_advancement_rating,
                 management_rating,
                 job_culture_rating), ~ifelse(. == 0, NA, .))

df$mean_rate <- rowMeans(cbind(df$job_work_and_life_balance_rating,
                               df$compensation_and_benefits_rating,
                               df$job_security_and_advancement_rating,
                               df$management_rating,
                               df$job_culture_rating), na.rm = TRUE)
  
# Combine year and month into a date
df_ca_tx <- df[df$state=='tx' | df$state=='ca',]

# Let's check our data
head(df)

######## Company Rating #########

# Calculate average rating by month for each state
avg_ratings <- df_ca_tx %>%
  mutate(month_year = floor_date(date, "month")) %>%
  group_by(state, month_year) %>%
  summarize(avg_rating = mean(rating, na.rm = TRUE))

# Get the range of years
years_range <- range(year(avg_ratings$month_year))

# Create a sequence of breaks for the x-axis
breaks <- seq(from = as.Date("2018-01-01", sep = ""), 
              to = as.Date("2023-01-01", sep = ""), 
              by = "year")

# Plot data
ggplot(avg_ratings, aes(x = month_year, y = avg_rating, color = state)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Average rating",
       title = "Company Rating by Month - Drivers & Shoppers",) +
  scale_color_discrete(name = "State") +
  theme_minimal()
# ggsave("images/Company Rating by Month - Drivers & Shoppers.jpeg", 
#        width = 11, height = 5, dpi = 350)

######## Mean Rating Across Domains #########

# Calculate average rating by month for each state
avg_ratings <- df_ca_tx %>%
  mutate(month_year = floor_date(date, "month")) %>%
  group_by(state, month_year) %>%
  summarize(avg_rating = mean(mean_rate, na.rm = TRUE))

# Plot data
ggplot(avg_ratings, aes(x = month_year, y = avg_rating, color = state)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Average rating",
       title = "Job Aspects Rating by Month - Drivers & Shoppers",) +
  scale_color_discrete(name = "State") +
  theme_minimal()
# ggsave("images/Job Aspects Rating by Month - Drivers & Shoppers.jpeg", 
#        width = 11, height = 5, dpi = 350)


######## VADER sentiment #########
# 1. sentiment from Germans (inclusing pros and cons)
# Calculate average rating by month for each state
avg_sentiments <- df_ca_tx %>%
  mutate(month_year = floor_date(date, "month")) %>%
  group_by(state, month_year) %>%
  summarize(avg_sentiment = mean(sentiment_vader, na.rm = TRUE))

# Plot data
ggplot(avg_sentiments, aes(x = month_year, y = avg_sentiment, color = state)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Average sentiment",
       title = "Reviews Sentiment by Month - Drivers & Shoppers",) +
  scale_color_discrete(name = "State") +
  theme_minimal()
# ggsave("images/Reviews Sentiment by Month - Drivers & Shoppers.jpeg",
#        width = 11, height = 5, dpi = 350)


# 2. sentiment from Sari (without pros and cons)

# Calculate average rating by month for each state
avg_sentiments <- df_full[df_full$is_driver==TRUE & 
                            (df_full$state=='ca'| df_full$state=='tx'),] %>%
  mutate(month_year = floor_date(date, "month")) %>%
  group_by(state, month_year) %>%
  summarize(avg_sentiment = mean(compound, na.rm = TRUE))

# Plot data
ggplot(avg_sentiments, aes(x = month_year, y = avg_sentiment, color = state)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Average sentiment",
       title = "Reviews Sentiment (excluding pros & cons) by Month - Drivers & Shoppers",) +
  scale_color_discrete(name = "State") +
  theme_minimal()
# ggsave("images/Reviews Sentiment (excluding pros & cons) by Month - Drivers & Shoppers.jpeg",
#        width = 11, height = 5, dpi = 350)

# 3. sentiment from Max (inclusing pros and cons)
# Calculate average rating by month for each state
df_ca_tx_full <- df_full[(df_full$state=='ca' | df_full$state=='tx') & 
                           df_full$is_driver==TRUE,]

avg_sentiments <- df_ca_tx_full %>%
  mutate(month_year = floor_date(date, "month")) %>%
  group_by(state, month_year) %>%
  summarize(avg_sentiment = mean(`NRC Disposition`, na.rm = TRUE))

# Plot data
ggplot(avg_sentiments, aes(x = month_year, y = avg_sentiment, color = state)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Average sentiment",
       title = "Reviews Sentiment by Month - Drivers & Shoppers",) +
  scale_color_discrete(name = "State") +
  theme_minimal()
# ggsave("images/Reviews Sentiment by Month - Drivers & Shoppers-NRC.jpeg",
#        width = 11, height = 5, dpi = 350)


######## Emotions in text #########
# 1. Emotions from Max - only California

# Calculate average rating by month
avg_emotions <- df_full[df_full$is_driver==TRUE & 
                          (df_full$state=='ca'),] %>%
  mutate(month_year = floor_date(date, "month")) %>%
  group_by(month_year) %>%
  summarize(avg_emotion = mean(`NRC Trust`, na.rm = TRUE))

# Plot data
p_trust <- ggplot(avg_emotions, aes(x = month_year, y = avg_emotion)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Trust",) +
  theme_minimal()

p_anger
p_anticipation
p_disgust
p_fear
p_joy
p_sadness
p_surprise
p_trust

library(patchwork)
# Arrange the plots
combined_plot <- p_anger + p_anticipation + p_disgust + p_fear + 
  p_joy + p_sadness + p_surprise + p_trust + 
  plot_layout(ncol = 4, nrow = 2)

# Add a title
combined_plot <- combined_plot & 
  plot_annotation(
    title = "Emotions Expressed in Reviews by Month",
    theme = theme(
      plot.title = element_text(hjust = 0.5)
    )
  )

# ggsave("images/Emotions Expressed in Reviews by Month.jpeg",
#        width = 14, height = 6, dpi = 350)


# 2. Emotions from Max - California vs. other states

df_full$is_ca <- 'CA'
df_full[c(df_full$state=="tx" | df_full$state=="ma" | df_full$state=="ny"),"is_ca"] <- "Other"

# Calculate average rating by month
avg_emotions <- df_full[df_full$is_driver==TRUE,] %>%
  mutate(month_year = floor_date(date, "month")) %>%
  group_by(is_ca, month_year) %>%
  summarize(avg_emotion = mean(`NRC Surprise`, na.rm = TRUE))

# Plot data
p_surprise <- ggplot(avg_emotions, aes(x = month_year, y = avg_emotion, color = is_ca)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Surprise",) +
  scale_color_discrete(name = "State") +
  theme_minimal()+
  theme(legend.position = "none")  # remove legend

p_anger
p_anticipation
p_disgust
p_fear
p_joy
p_sadness
p_surprise
p_trust

library(gridExtra)
library(gtable)

# Combine the plots
combined_plot <- arrangeGrob(p_anger, p_anticipation, p_disgust, p_fear, 
                             p_joy, p_sadness, p_surprise, p_trust, 
                             ncol = 4, nrow = 2)

# Extract legend from one of the plots (with legend)
p_with_legend <- ggplot(avg_emotions, aes(x = month_year, y = avg_emotion, color = is_ca)) +
  geom_line() +
  geom_smooth(method = "loess") +
  geom_vline(xintercept = as.numeric(as.Date("2021-01-01")), linetype="dashed", 
             color = "black", size=1) +
  scale_x_date(breaks = breaks, date_labels = "%Y") +  # control x-axis breaks and labels
  labs(x = "Date", y = "Trust") +
  scale_color_discrete(name = "State", guide = guide_legend(nrow = 1)) +
  theme_minimal()

# Extract legend
legend <- gtable::gtable_filter(ggplotGrob(p_with_legend), "guide-box") 

# Add a title
title <- grid::textGrob("Emotions Expressed in Reviews by Month by State", 
                        gp = grid::gpar(fontsize = 20))

# Combine the plots, the title, and the legend
final_plot <- gridExtra::arrangeGrob(title, combined_plot, legend, 
                                     nrow = 3, heights = c(1, 10, 1))

# Print the final plot
grid::grid.newpage()
grid::grid.draw(final_plot)

# or with grDevices
grDevices::png(file = "images/Emotions Expressed in Reviews by Month by State - one_legend.jpeg",
               width = 16, height = 7, units = "in", res = 300)
grid::grid.draw(final_plot)
dev.off() 

######## Anova 2020 vs. 2021 #########

# compare reviewers' ratings in ca vs. other
df_full_20_21 <- df_full[df_full$year==2020 | df_full$year==2021, ]
df_full_20_21$year <- as.factor(df_full_20_21$year)

my_aov <- aov(`NRC Anticipation` ~ year*is_ca, data=df_full_20_21)
summary(my_aov)

# Compute means for each group
df_means <- df_full_20_21 %>%
  group_by(year, is_ca) %>%
  summarise(mean_rating = mean(compensation_and_benefits_rating, na.rm = TRUE))

# Plot
ggplot(df_means, aes(x = year, y = mean_rating, fill = is_ca)) +
  geom_bar(stat = "identity", position = "dodge") +
  #ylim(1, 5) +  # Set y-axis limits
  theme_minimal() +
  labs(x = "Year", y = "Average Work-Life Balance Rating", 
       title = "ANOVA Results: Work-Life Balance by Year and State",
       fill = "State")

# interaction is only significant for compensation

######### Correlation Matrix #########
# Load required libraries
library(ggcorrplot)

# Choose variables of interest
vars_4_cor <- as.data.frame(cbind(df_full$rating, 
                                  df_full$mean_rate, 
                                  df_full$sentiment_vader, 
                                  df_full$`NRC Disposition`,
                                  df_full$`NRC Anger`,
                                  df_full$`NRC Joy`))
# Define custom labels
names(vars_4_cor) <- c("General rating", "Average aspect rating", 
                        "VADER sentiment", "NRC sentiment", "NRC anger", "NRC joy")


# Calculate correlation matrix
corr_matrix <- cor(vars_4_cor, use = "pairwise.complete.obs") # use can be everything, complete.obs or pairwise.complete.obs


# Plot correlation matrix with custom labels
ggcorrplot(corr_matrix,
           lab = TRUE,
           hc.order = TRUE,
           type = "lower",
           method = "square",
           colors = c("#6D9EC1", "white", "#E46726"),
           title = "Correlation Matrix of Variables")
