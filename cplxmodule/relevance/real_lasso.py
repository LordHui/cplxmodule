import torch
from torch.nn import Linear

from cplxmodule.relevance.base import BaseARD, SparseModeMixin


class LinearLASSO(Linear, BaseARD, SparseModeMixin):
    def __init__(self, in_features, out_features, bias=True, reduction="mean"):
        super().__init__(in_features, out_features, bias=bias)
        self.reduction = reduction

    def forward(self, input):
        if self.is_sparse:
            return self.forward_sparse(input)

        return super().forward(input)

    @property
    def penalty(self):
        w_norm = abs(self.weight)
        if self.reduction == "mean":
            return w_norm.mean()

        elif self.reduction == "sum":
            return w_norm.sum()

        return w_norm

    def get_sparsity_mask(self, threshold):
        with torch.no_grad():
            # the mask is $\tau \mapsto \lvert w_{ij} \rvert \leq \tau$
            return torch.le(abs(self.weight), threshold)

    def num_zeros(self, threshold):
        return self.get_sparsity_mask(threshold).sum().item()