import ppgs
import torch

###############################################################################
# Model selection
###############################################################################


def Model(type=None):
    type = ppgs.MODEL if type is None else type
    if type == 'convolution':
        print('using convolutional model')
        return ppgs.model.Convolution
    elif type == 'transformer':
        print('using transformer model')
        return lambda: ppgs.model.LengthsWrapperModel(
            [
                torch.nn.Conv1d(ppgs.INPUT_CHANNELS, ppgs.HIDDEN_CHANNELS, kernel_size=ppgs.KERNEL_SIZE, padding="same"),
                ppgs.model.Transformer(),
                torch.nn.Conv1d(ppgs.HIDDEN_CHANNELS, len(ppgs.PHONEME_LIST), kernel_size=ppgs.KERNEL_SIZE, padding="same")
            ],
            [False, True, False]
        )
    raise ValueError('unknown model type:', type)
