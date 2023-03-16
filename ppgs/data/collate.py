import torch

def reduced_collate(batch):
    """Batch collation with reduced features"""
    input_ppgs, indices = zip(*batch)
    channels, _ = input_ppgs[0].shape
    lengths = torch.tensor([ppg.shape[-1] for ppg in input_ppgs], dtype=torch.long)
    max_length = lengths.max().item()
    batch = len(input_ppgs)

    padded_ppgs = torch.zeros(
        (batch, channels, max_length),
        dtype=torch.float
    )

    # Allocate padded target phoneme indices
    # -100 is the default ignore_index value for cross entropy loss
    padded_indices = torch.full((batch, max_length), -100, dtype=torch.long)

    # Populate padded tensors
    for i, (ppg, index) in enumerate(zip(input_ppgs, indices)):
        padded_ppgs[i, :, :ppg.shape[-1]] = ppg
        padded_indices[i, :ppg.shape[-1]] = index

    return padded_ppgs, padded_indices, lengths

def collate(batch):
    """Batch collation"""
    # Unpack
    input_ppgs, indices, alignments, word_breaks, waveforms, stems = zip(*batch)

    # Get padded tensor dimensions
    channels, _ = input_ppgs[0].shape
    max_length = max([ppg.shape[-1] for ppg in input_ppgs])
    batch = len(input_ppgs)

    # Allocate padded input ppgs
    padded_ppgs = torch.zeros(
        (batch, channels, max_length),
        dtype=torch.float)

    # Allocate padded target phoneme indices
    # -100 is the default ignore_index value for cross entropy loss
    padded_indices = torch.full((batch, max_length), -100, dtype=torch.long)

    # Populate padded tensors
    for i, (ppg, index) in enumerate(zip(input_ppgs, indices)):
        padded_ppgs[i, :, :ppg.shape[-1]] = ppg
        padded_indices[i, :ppg.shape[-1]] = index

    return padded_ppgs, padded_indices, alignments, word_breaks, waveforms, stems
