# Accuracy: official split, pooled split and the best-possible ceiling

Scheme `current`, whole-pool tier; mean +/- std over seeds. The ceiling is what ANY classifier could reach on the pool's raw columns (rows with identical feature vectors can only get one label); it is not a target for the model.

| pool | hyperparameters | official split | pooled random split | ceiling | official - ceiling | pooled - ceiling |
|---|---|---|---|---|---|---|
| 40f | default | 0.7427 +/- 0.0009 | 0.8305 +/- 0.0009 | 0.9117 | -0.1690 | -0.0812 |
| 48f | default | 0.7401 +/- 0.0020 | 0.8493 +/- 0.0010 | 0.9212 | -0.1811 | -0.0719 |
| 45f | default | 0.7367 +/- 0.0015 | 0.8470 +/- 0.0008 | 0.9212 | -0.1845 | -0.0742 |
