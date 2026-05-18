# SatNOGS Post-Pass Report

Build a compact post like:

```text
SatNOGS post-pass data report for station 984

- ID: 13884987
  ground_station: 984
  sat_id: UBGG-0313-1046-0311-8192
  start: 2026-04-23T10:19:12Z
  end: 2026-04-23T10:27:21Z
  observation_frequency: 145850000 (145.850 MHz)
  payload: https://...
  waterfall: https://...
  status: unknown
```

## Script

`scripts/satnogs_post_report.py`

## Example

```bash
python3 scripts/satnogs_post_report.py \
  --id 13884987 --ground-station 984 --sat-id UBGG-0313-1046-0311-8192 \
  --start 2026-04-23T10:19:12Z --end 2026-04-23T10:27:21Z \
  --observation-frequency 145850000 \
  --payload https://network-satnogs.freetls.fastly.net/media/data_obs/2026/4/23/10/13884987/satnogs_13884987_2026-04-23T10-19-12.ogg \
  --waterfall https://s3.eu-central-1.wasabisys.com/satnogs-network/data_obs/2026/4/23/10/13884987/waterfall_13884987_2026-04-23T10-19-12.png \
  --status unknown
```

## Notes

- Keep the output plain Markdown for Discord.
- Use `--json file.json` if the report starts from API data.
