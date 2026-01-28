# ---- Libraries ----

# Define all required packages
packages <- c(
  # Data importing
  "readxl", "writexl", "googlesheets4",

  # Data wrangling
  "labelled", "tidyverse", "janitor", "formattable",

  # Visualization
  "ggThemeAssist", "esquisse", "ggstatsplot",
  "ggthemes", "ggsignif", "GGally", "ggeffects", "corrplot", "viridis",

  # Descriptive statistics
  "summarytools", "skimr", "gtsummary", "gt",

  # Statistical analysis
  "rstatix",

  # Survival analysis
  "survival", "survminer",

  # Utilities
  "patchwork", "questionr", "cutpointr", "rankinPlot",
  "haven", "SmartEDA", "dlookr", "MASS", "ordinal", "tools", "broom", "conflicted",

  # Regression
  "equatiomatic",

  # Reporting
  "knitr", "kableExtra", "flextable", "report"
)

# Install missing packages
missing <- packages[!packages %in% installed.packages()[,"Package"]]
if (length(missing) > 0) {
  install.packages(missing)
}
if (exists("missing")) rm(missing)

# Load all packages quietly
invisible(lapply(packages, library, character.only = TRUE))

#  Manually reload key packages with comments
library(summarytools)   # descriptive statistics and dataframe summaries
library(ggstatsplot)    # ggplot2 with embedded statistical tests
library(gtsummary)      # publication-ready summary tables
library(survminer)      # Kaplan-Meier and survival plots
library(equatiomatic)   # turn models into equations
library(knitr)          # knit reports
library(kableExtra)     # enhanced tables for reports

library(conflicted)
conflict_prefer("select", "dplyr")
conflict_prefer("filter", "dplyr")


# TO INSTALL: source("env/r-packages.R")
