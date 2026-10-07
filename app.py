from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="NYC Airbnb explorer", page_icon="🏙️", layout="wide")

BASE = "#8FB3D1"        # normal bars
HIGHLIGHT = "#E4572E"   # the biggest bar
TEXT = "#1F2937"
LINE = "#D1D5DB"

ROOM_ENTIRE = "Entire home/apt"


# ---------------------------------------------------------------- data
@st.cache_data
def load_data():
    path = Path(__file__).parent / "nyc_airbnb_clean.csv"
    return pd.read_csv(path, parse_dates=["last_review"])


# --------------------------------------------------------------- charts
def bar_chart(data, title, prefix="", fmt="{:,.0f}", suffix="", horizontal=False, highlight=True):
    """One simple bar chart. The value is written on every bar; the biggest bar is highlighted."""
    data = data.dropna()
    if data.empty:
        st.info("Not enough listings to draw this chart with the current filters.")
        return

    labels = [f"{prefix}{fmt.format(v)}{suffix}" for v in data.values]
    colors = [BASE] * len(data)
    if highlight:
        colors[int(data.values.argmax())] = HIGHLIGHT
    names = [str(i) for i in data.index]

    if horizontal:
        fig, ax = plt.subplots(figsize=(6.5, 0.46 * len(data) + 1.3))
        bars = ax.barh(names[::-1], data.values[::-1], color=colors[::-1])
        ax.bar_label(bars, labels=labels[::-1], padding=4, fontsize=11, color=TEXT)
        ax.margins(x=0.22)
        ax.xaxis.set_visible(False)
        keep = "left"
    else:
        fig, ax = plt.subplots(figsize=(6.5, 4))
        bars = ax.bar(names, data.values, color=colors)
        ax.bar_label(bars, labels=labels, padding=3, fontsize=11, color=TEXT)
        ax.margins(y=0.16)
        ax.yaxis.set_visible(False)
        if len(names) > 5 or max(len(n) for n in names) > 10:
            plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
        keep = "bottom"

    fig.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold", color=TEXT)
    ax.tick_params(length=0, labelsize=10.5, labelcolor=TEXT)
    ax.grid(False)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side == keep)
        ax.spines[side].set_color(LINE)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    st.pyplot(fig)
    plt.close(fig)


def share(series_mask):
    """Percentage of True values."""
    return series_mask.mean() * 100


# ----------------------------------------------------------------- page
df = load_data()
valid_prices = df[df.price_valid == 1].price
zero_price_count = int((df.price_valid == 0).sum())

st.title("New York City Airbnb listings")
st.write("See what is listed, what it costs and who hosts it. Use the filters on the left to narrow it down.")

# ------------------------------------------------------------- filters
st.sidebar.header("Filter the listings")

boroughs = sorted(df.neighbourhood_group.unique())
chosen_boroughs = st.sidebar.multiselect("Borough", boroughs, default=boroughs)

room_types = sorted(df.room_type.unique())
chosen_rooms = st.sidebar.multiselect("Type of place", room_types, default=room_types)

pmin, pmax = int(valid_prices.min()), int(valid_prices.max())
price_low, price_high = st.sidebar.slider("Price per night ($)", pmin, pmax, (pmin, pmax), step=10)

hide_inactive = st.sidebar.checkbox(
    "Hide listings that look inactive",
    value=False,
    help="Inactive here means: no open dates in the next year and no guest review since 2018.",
)

f = df[
    df.neighbourhood_group.isin(chosen_boroughs)
    & df.room_type.isin(chosen_rooms)
    & (df.price_valid == 1)
    & df.price.between(price_low, price_high)
]
if hide_inactive:
    f = f[f.likely_dormant == 0]

if f.empty:
    st.warning("No listings match these filters. Widen the filters on the left to see results.")
    st.stop()

n = len(f)

# ----------------------------------------------------------- number cards
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Listings", f"{n:,}")
c2.metric("Typical price per night", f"${f.price.median():,.0f}",
          help="The middle price: half of the listings cost less, half cost more.")
c3.metric("Entire homes", f"{share(f.room_type == ROOM_ENTIRE):.0f}%",
          help="Share of listings where guests get the whole place to themselves.")
c4.metric("Have a guest review", f"{share(f.has_review == 1):.0f}%",
          help="Share of listings with at least one review.")
c5.metric("Closed for the year", f"{share(f.is_closed == 1):.0f}%",
          help="Share of listings with no open dates in the next 365 days.")

st.divider()

tab_market, tab_prices, tab_hosts, tab_activity, tab_map = st.tabs(
    ["The market", "Prices", "Hosts", "Activity", "Map"]
)

# ------------------------------------------------------------ the market
with tab_market:
    by_borough = f.neighbourhood_group.value_counts()
    by_room = f.room_type.value_counts()
    median_by_borough = f.groupby("neighbourhood_group").price.median().sort_values(ascending=False)

    st.write(
        f"**{by_borough.index[0]}** has the most listings, with {by_borough.iloc[0] / n * 100:.0f}% of the total. "
        f"The most common type of place is **{by_room.index[0].lower()}** ({by_room.iloc[0] / n * 100:.0f}%). "
        f"**{median_by_borough.index[0]}** has the highest typical price, at ${median_by_borough.iloc[0]:,.0f} per night."
    )

    left, right = st.columns(2)
    with left:
        bar_chart(by_borough, "Number of listings by borough")
    with right:
        bar_chart(by_room / n * 100, "Share of listings by type of place", fmt="{:.0f}", suffix="%")

    left, right = st.columns(2)
    with left:
        bar_chart(median_by_borough, "Typical price per night by borough", prefix="$")

# ---------------------------------------------------------------- prices
with tab_prices:
    bands = [0, 49, 99, 149, 199, 299, 499, 5000]
    band_names = ["Under $50", "$50-99", "$100-149", "$150-199", "$200-299", "$300-499", "$500+"]
    price_band = pd.cut(f.price, bands, labels=band_names).value_counts().reindex(band_names)
    median_by_room = f.groupby("room_type").price.median().sort_values(ascending=False)

    hood = f.groupby("neighbourhood").price.agg(["median", "size"])
    hood = hood[hood["size"] >= 30].sort_values("median", ascending=False)
    busiest = f.neighbourhood.value_counts().head(10)

    st.write(
        f"Half of the listings cost **${f.price.median():,.0f}** per night or less. "
        f"**{median_by_room.index[0]}** is the most expensive type of place, "
        f"at a typical ${median_by_room.iloc[0]:,.0f}."
    )

    left, right = st.columns(2)
    with left:
        bar_chart(price_band / n * 100, "Share of listings by price per night", fmt="{:.0f}", suffix="%")
    with right:
        bar_chart(median_by_room, "Typical price per night by type of place", prefix="$")

    left, right = st.columns(2)
    with left:
        if len(hood) >= 3:
            bar_chart(hood["median"].head(10), "10 most expensive neighbourhoods (typical price)",
                      prefix="$", horizontal=True)
            st.caption("Only neighbourhoods with at least 30 listings are included.")
        else:
            st.info("Too few neighbourhoods with 30 or more listings for this chart.")
    with right:
        bar_chart(busiest, "10 neighbourhoods with the most listings", horizontal=True)

# ----------------------------------------------------------------- hosts
with tab_hosts:
    host_bins = [0, 1, 2, 5, 1000]
    host_names = ["1 listing", "2 listings", "3-5 listings", "6 or more"]
    host_size = pd.cut(f.calculated_host_listings_count, host_bins, labels=host_names)
    host_share = host_size.value_counts().reindex(host_names) / n * 100
    entire_by_host = f.groupby(host_size, observed=False).room_type.apply(
        lambda s: share(s == ROOM_ENTIRE) if len(s) else float("nan")
    ).reindex(host_names)

    single = share(f.calculated_host_listings_count == 1)
    large = share(f.calculated_host_listings_count >= 6)
    st.write(
        f"**{single:.0f}%** of the listings belong to hosts who only have one listing. "
        f"Hosts with 6 or more listings own {large:.0f}% of the listings."
    )

    left, right = st.columns(2)
    with left:
        bar_chart(host_share, "Share of listings by how many listings the host has",
                  fmt="{:.0f}", suffix="%")
    with right:
        bar_chart(entire_by_host, "Share that are entire homes, by host size",
                  fmt="{:.0f}", suffix="%")

# -------------------------------------------------------------- activity
with tab_activity:
    avail_bins = [-1, 0, 90, 180, 270, 365]
    avail_names = ["Closed all year", "1-90 days open", "91-180 days open", "181-270 days open", "271-365 days open"]
    avail = pd.cut(f.availability_365, avail_bins, labels=avail_names).value_counts().reindex(avail_names) / n * 100
    closed_by_borough = f.groupby("neighbourhood_group").is_closed.mean().mul(100).sort_values(ascending=False)
    last_review_order = ["Reviewed in 2019", "Reviewed in 2018", "Reviewed 2017 or earlier", "Never reviewed"]
    last_review = f.activity_status.value_counts().reindex(last_review_order).fillna(0) / n * 100

    inactive = share(f.likely_dormant == 1)
    st.write(
        f"**{share(f.is_closed == 1):.0f}%** of the listings have no open dates in the next year. "
        f"**{inactive:.0f}%** look inactive: they are closed and have had no guest review since 2018."
    )

    left, right = st.columns(2)
    with left:
        bar_chart(avail, "How many days a year listings are open", fmt="{:.0f}", suffix="%")
    with right:
        bar_chart(closed_by_borough, "Share of listings closed all year, by borough", fmt="{:.0f}", suffix="%")

    left, right = st.columns(2)
    with left:
        bar_chart(last_review, "When listings last got a guest review", fmt="{:.0f}", suffix="%", highlight=False)

# ------------------------------------------------------------------- map
with tab_map:
    st.write("Each dot is one listing. The map shows a random sample of up to 5,000 of the listings you selected.")
    sample = f.sample(min(5000, n), random_state=1)
    st.map(sample[["latitude", "longitude"]], size=12)

# ----------------------------------------------------------------- about
with st.expander("About this data"):
    st.write(
        "- The data is a public list of New York City Airbnb listings from mid-2019. The latest review is dated July 2019.\n"
        "- There are no booking records. A guest review is used as a sign that a listing is being used.\n"
        "- Typical price means the middle price, so a few very expensive listings do not pull it up.\n"
        f"- {zero_price_count} listings with a $0 price are left out because $0 is not a real nightly price."
    )
