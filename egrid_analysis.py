import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile  # Added to handle temporary file creation

# Read the dataset (assuming file path is correct)
egrid = pd.read_csv("egrid2016.csv")

# Ensure that 'NAMEPCAP' is numeric, converting non-numeric values to NaN
egrid["NAMEPCAP"] = pd.to_numeric(egrid["NAMEPCAP"], errors="coerce")
# Drop rows where 'NAMEPCAP' is NaN
egrid.dropna(subset=["NAMEPCAP"], inplace=True)

# Generate summary statistics (mean, median, standard deviation)
state_capacity_mean = egrid[["PSTATABB", "NAMEPCAP"]].groupby("PSTATABB").mean()
state_capacity_median = egrid[["PSTATABB", "NAMEPCAP"]].groupby("PSTATABB").median()
state_capacity_std = egrid[["PSTATABB", "NAMEPCAP"]].groupby("PSTATABB").std()

# Combine summary statistics into one table
statistics_summary = pd.concat(
    [state_capacity_mean, state_capacity_median, state_capacity_std], axis=1
)
statistics_summary.columns = ["Mean", "Median", "Std Dev"]
summary_text = statistics_summary.to_string()  # Convert to string for PDF output

# Plot the top 5 states by capacity
top_capacity = state_capacity_mean.sort_values("NAMEPCAP", ascending=False).head()
states_top_capacity = top_capacity.index
capacity_values = top_capacity["NAMEPCAP"]

# Create the bar chart and save to a temporary file
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
    plt.figure()
    plt.bar(states_top_capacity, capacity_values)
    plt.title("Top 5 States by Capacity (NAMEPCAP)")
    plt.xlabel("State (PSTATABB)")
    plt.ylabel("Capacity (NAMEPCAP)")
    plt.savefig(tmp_file.name)
    plt.close()  # Close the figure to avoid displaying

    # Create a PDF document
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EGRID Data Report", ln=True, align="C")

    # Add some space
    pdf.ln(10)

    # Add the summary statistics
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="Summary Statistics (Mean, Median, Standard Deviation):")
    pdf.ln(5)  # Line break

    # Add the actual statistics summary
    pdf.set_font("Courier", size=10)
    pdf.multi_cell(0, 10, txt=summary_text)

    # Add some space before the plot
    pdf.ln(10)

    # Insert the plot from the temporary file
    pdf.image(tmp_file.name, x=10, y=None, w=190)  # Adjust the width as needed

    # Save the PDF to a file
    pdf.output("egrid_report.pdf")

    print("PDF has been created successfully.")
