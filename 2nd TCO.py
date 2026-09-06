import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fleet TCO Calculator", page_icon="🚌", layout="wide")

def calculate_tco(
    beb_purchase,
    fceb_purchase,
    beb_maintenance,
    fceb_maintenance,
    beb_efficiency,
    fceb_efficiency,
    electricity_price,
    hydrogen_price,
    lifetime_miles,
):
    # battery
    beb_energy_per_mile = beb_efficiency * electricity_price
    beb_energy_total = beb_energy_per_mile * lifetime_miles
    beb_maintenance_total = beb_maintenance * lifetime_miles
    beb_total = beb_purchase + beb_energy_total + beb_maintenance_total

    # hydrogen
    hydrogen_per_mile = hydrogen_price / fceb_efficiency
    hydrogen_energy_total = hydrogen_per_mile * lifetime_miles
    hydrogen_maintenance_total = fceb_maintenance * lifetime_miles
    fceb_total = fceb_purchase + hydrogen_energy_total + hydrogen_maintenance_total

    return beb_total, fceb_total


st.title("Fleet Total Cost of Ownership")
st.caption(
    "Compare lifetime cost for battery-electric and hydrogen fuel-cell buses "
    "under adjustable purchase, maintenance, and fuel assumptions."
)

with st.expander("About this model — origin, question, and findings", expanded=True):
    st.markdown(
        """
### The result, up front
At current lifetime-mile and maintenance assumptions, hydrogen becomes cost-competitive
with battery-electric once hydrogen prices fall to roughly **$[X.XX]/kg**
*(replace with your model's actual break-even — read it off the chart below where the
two lines cross)*. At today's typical hydrogen prices, **[battery-electric / hydrogen]**
comes out ahead over the bus's lifetime.

**What that means practically:** [e.g., "At current hydrogen prices, battery-electric
wins unless hydrogen production costs drop substantially — which would require X, Y, or Z
to happen (cheaper electrolysis, subsidies, regional production, etc.)."]

### Where this came from
This model started with a question raised by the **[Youth Advisory Committee]** to
**Rep. [Torres]**: [one or two sentences on what was actually asked — e.g., "why is our
district's transit authority choosing battery buses over hydrogen, and is that actually
the cheaper option long-term?"]. That conversation is what led to building a model that
could answer it with real numbers instead of assumptions.

### The question this model answers
At what hydrogen price ($/kg) does a hydrogen fuel-cell bus become cheaper, over its
full lifetime, than a battery-electric bus?

### How the model works
Total cost of ownership for each bus type is built from three pieces:
- **Capital cost** — upfront purchase price of the bus
- **Operating cost** — maintenance cost per mile × lifetime miles
- **Energy cost** — for battery buses, efficiency (kWh/mile) × electricity price; for
  hydrogen buses, efficiency (miles/kg) and hydrogen price ($/kg), converted to a
  per-mile cost

All three are summed to get each bus type's lifetime total, then compared directly
against each other and, in the chart below, across a full range of hydrogen prices.

        """
    )


with st.sidebar:
    st.header("Battery-electric bus (BEB)")
    beb_purchase = st.slider("Purchase price ($)", 500_000, 1_200_000, 850_000, 10_000)
    beb_maintenance = st.slider("Maintenance ($/mile)", 0.10, 2.00, 0.90, 0.01)
    beb_efficiency = st.slider("Efficiency (kWh/mile)", 1.0, 5.0, 2.5, 0.1)
    electricity_price = st.slider("Electricity price ($/kWh)", 0.05, 0.50, 0.15, 0.01)

    st.header("Hydrogen fuel-cell bus (FCEB)")
    fceb_purchase = st.slider("Purchase price ($) ", 500_000, 1_500_000, 1_000_000, 10_000)
    fceb_maintenance = st.slider("Maintenance ($/mile) ", 0.10, 2.00, 0.70, 0.01)
    fceb_efficiency = st.slider("Efficiency (miles/kg)", 3.0, 15.0, 8.0, 0.1)
    hydrogen_price = st.slider("Hydrogen price ($/kg)", 1.0, 20.0, 8.0, 0.25)

    st.header("Shared")
    lifetime_miles = st.slider("Lifetime miles", 100_000, 1_000_000, 500_000, 10_000)

beb_total, fceb_total = calculate_tco(
    beb_purchase,
    fceb_purchase,
    beb_maintenance,
    fceb_maintenance,
    beb_efficiency,
    fceb_efficiency,
    electricity_price,
    hydrogen_price,
    lifetime_miles,
)
difference = abs(beb_total - fceb_total)
recommendation = "Battery Electric Bus" if beb_total < fceb_total else "Hydrogen Fuel Cell Bus"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Battery TCO", f"${beb_total:,.0f}")
col2.metric("Hydrogen TCO", f"${fceb_total:,.0f}")
col3.metric("Difference", f"${difference:,.0f}")
col4.metric("Recommendation", recommendation)

st.subheader("Sensitivity to hydrogen price")
st.caption(
    "Hydrogen TCO traced across $1–$20/kg, all other inputs held at current slider values. "
    "Battery TCO shown as a flat reference line."
)

prices = np.linspace(1, 20, 100)
hydrogen_costs = []
for price in prices:
    _, hydrogen_total = calculate_tco(
        beb_purchase,
        fceb_purchase,
        beb_maintenance,
        fceb_maintenance,
        beb_efficiency,
        fceb_efficiency,
        electricity_price,
        price,
        lifetime_miles,
    )
    hydrogen_costs.append(hydrogen_total)

chart_df = pd.DataFrame(
    {
        "Hydrogen Bus": hydrogen_costs,
        "Battery Bus": [beb_total] * len(prices),
    },
    index=pd.Index(prices, name="Hydrogen Price ($/kg)"),
)
st.line_chart(chart_df)
