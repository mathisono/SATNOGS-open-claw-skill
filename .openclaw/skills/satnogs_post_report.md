# SatNOGS Post-Pass Report

Compact formatter for SatNOGS observation data.

## Script

`python3 scripts/satnogs_post_report.py`

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

- Plain Markdown output.
- `--json file.json` works too.
- Local-model friendly.
