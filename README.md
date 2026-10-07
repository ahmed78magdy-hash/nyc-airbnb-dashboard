# NYC Airbnb Listings Dashboard

A simple, filterable dashboard of 48,808 New York City Airbnb listings. It shows what is listed, what it costs, who hosts it and how active the listings are, with plain bar charts anyone can read.

**Live app:** [ADD-YOUR-LIVE-APP-LINK-HERE](ADD-YOUR-LIVE-APP-LINK-HERE)

## What the dashboard shows

| Tab | Question it answers |
|---|---|
| The market | Where are the listings, and what kind of places are they? |
| Prices | What does a night cost, and which neighbourhoods are the most expensive? |
| Hosts | Are listings run by individuals or by large operators? |
| Activity | How many listings are open for booking, and how many look inactive? |
| Map | Where is each listing? |

Filters on the left: borough, type of place, price per night, and an option to hide listings that look inactive.

## Key findings

- **Two boroughs hold most of the market.** Manhattan (21,621 listings) and Brooklyn (20,076) make up 85% of all listings.
- **The typical price is $106 per night.** Manhattan is $150, Brooklyn $90, Queens and Staten Island $75, the Bronx $65.
- **Entire homes are the most common type** (52%), followed by private rooms (46%). Shared rooms are 2%.
- **Most hosts are individuals.** 86% of hosts have one listing, and those listings are 66% of the total. Hosts with 6 or more listings own 10%.
- **A third of the listings are closed.** 36% have no open dates in the next year, and 23% (11,067 listings) look inactive: closed, with no guest review since 2018.
- **Very expensive listings are reviewed less often.** 60% of listings priced at $500 or more have a review, compared with about 82% in the $50 to $149 range.

## Data

- Public New York City Airbnb listings, a snapshot from mid-2019. The latest review is dated 8 July 2019.
- 48,895 listings in the raw file, 48,819 after cleaning.

| Step | Result |
|---|---|
| Duplicate listings | None found |
| Extreme values removed | 40 listings (price of $5,000 or more, or a minimum stay over 365 nights) |
| Missing listing or host name removed | 36 listings |
| Listings with a $0 price | 11, kept in the data but left out of price figures |
| Listing names with stray spaces or line breaks | 235, cleaned |

Listing and host names are not included in this repository's data file.

## Limits to keep in mind

- There are no booking records. A guest review is used as a sign that a listing is being used.
- "Typical price" is the middle price, so a few very expensive listings do not pull it up.
- "Closed" means no open dates in the next 365 days. A fully booked listing would also show as closed.
- The data is from 2019 and does not describe the market today.

## Tools

MySQL for importing and cleaning, Python (pandas, matplotlib) for analysis, Streamlit for the dashboard, GitHub and Streamlit Community Cloud for hosting.

## Run it on your computer

```
pip install -r requirements.txt
streamlit run app.py
```

Keep `app.py` and `nyc_airbnb_clean.csv` in the same folder.

## Author

Ahmed, [github.com/ahmed78magdy-hash](https://github.com/ahmed78magdy-hash)
