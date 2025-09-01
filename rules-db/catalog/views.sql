\
CREATE TABLE IF NOT EXISTS rules_jsonl (json TEXT);
CREATE VIEW IF NOT EXISTS rules AS
SELECT
  json_extract(json,'$.uid') AS uid,
  json_extract(json,'$.source') AS source,
  json_extract(json,'$.language') AS language,
  json_extract(json,'$.rule_id') AS rule_id,
  json_extract(json,'$.name') AS name,
  json_extract(json,'$.category') AS category,
  json_extract(json,'$.severity') AS severity,
  json_extract(json,'$.quality.adaptability') AS q_adapt,
  json_extract(json,'$.quality.consistency') AS q_cons,
  json_extract(json,'$.quality.intentionality') AS q_intent,
  json_extract(json,'$.quality.responsibility') AS q_resp
FROM rules_jsonl;
