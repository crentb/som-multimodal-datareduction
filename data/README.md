# `data/general_main.csv`

138 multimodal measurements of tooth enamel used to train the SOM. Each row is one
indentation/measurement site on a tooth, combining mechanical, chemical (Raman), and
fracture data with specimen metadata. This is the dataset behind:

> C. Renteria, W. Yan, Y. L. Huang, D. D. Arola, "Contributions to enamel durability
> with aging: An application of data science tools," *J. Mech. Behav. Biomed. Mater.*
> 129, 105147 (2022). doi:10.1016/j.jmbbm.2022.105147

Please cite that paper if you use this data. For exact measurement protocols and units,
see the paper; the summary below documents each column's role in the pipeline.

## Columns

| Column | Type | Role | Description |
|--------|------|------|-------------|
| `Row` | int | id | Per-measurement identifier (1…138); carried through to the maps as the point label. |
| `modulus` | float | **feature** | Elastic (reduced) modulus from nanoindentation. |
| `hardness` | float | **feature** | Hardness from nanoindentation. |
| `carb` | float | **feature** | Raman carbonate marker (carbonate-to-phosphate ratio). |
| `crys` | float | **feature** | Raman crystallinity marker (inverse phosphate ν1 peak width). |
| `fluo` | float | **feature** | Raman fluorescence / background position (~960 cm⁻¹ region). |
| `depth` | float | **feature** | Normalized depth from the enamel surface (0 = inner … 1 = outer, study-relative). |
| `kc` | float | **feature** | Fracture toughness. |
| `b` | float | **feature** | Fitted crack-growth-resistance (R-curve) parameter. |
| `age` | int | metadata | Age of the specimen (years; species-relative). |
| `tooth_label` | str | metadata | Tooth/specimen code. |
| `mammal` | str | metadata | Species group (e.g. `h` = human, `o` = other). |
| `age_group` | str | metadata | Cohort code (human `p`/`y`/`o` = primary/young/old; plus animal codes such as `lion`, `sl`, `wad`, …). |
| `position` | str | metadata | Through-thickness location: `outer` / `middle` / `inner`. |

The eight **feature** columns are the SOM's default training set
(`som_multimodal.config.DEFAULT_FEATURES`); the metadata columns are not used for
training but ride along in the HDF5 file and can color the cluster map
(`--label-column`, default `mammal`).
