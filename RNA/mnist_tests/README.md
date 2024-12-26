# Testing MLP architectures, parameters and DA

- Basic MLP AC: 98.34%

## Batch Normalization

- 1 layer per RELU: 98.64%

## Optimizer 

- SDG (all other results)
- ADAM: 98.33% (with batch Normalization)

## LR

- Linear: 98.74  in epoch  58
- Plateau: 98.61  in epoch  45

## Data augmentation

- Rotation 98.99  in epoch  45
- Elastic Transform 99.29  in epoch  45
- Augmix 99.14% in epoch  32
- da4 99.16  in epoch  48
- 99.46  in epoch  46



