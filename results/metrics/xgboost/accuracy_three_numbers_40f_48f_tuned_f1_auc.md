# Accuracy: official split, pooled split and the best-possible ceiling

Scheme `current`, whole-pool tier; mean +/- std over seeds. The ceiling is what ANY classifier could reach on the pool's raw columns (rows with identical feature vectors can only get one label); it is not a target for the model.

| pool | hyperparameters | official split | pooled random split | ceiling | official - ceiling | pooled - ceiling |
|---|---|---|---|---|---|---|
| 40f | default | 0.7427 +/- 0.0009 | 0.8305 +/- 0.0009 | 0.9117 | -0.1690 | -0.0812 |
| 40f | tuned_f1 | 0.7514 +/- 0.0019 | n/a | 0.9117 | -0.1603 | n/a |
| 40f | tuned_auc | 0.7647 +/- 0.0010 | n/a | 0.9117 | -0.1470 | n/a |
| 48f | default | 0.7401 +/- 0.0020 | 0.8493 +/- 0.0010 | 0.9212 | -0.1811 | -0.0719 |
| 48f | tuned_f1 | 0.7591 +/- 0.0012 | n/a | 0.9212 | -0.1621 | n/a |
| 48f | tuned_auc | 0.7591 +/- 0.0012 | n/a | 0.9212 | -0.1621 | n/a |
