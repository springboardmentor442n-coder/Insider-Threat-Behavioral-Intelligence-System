"""
BehavioralIntelligenceNet — matches the uploaded behavioral_intelligence_model.pth exactly.

Architecture (reverse-engineered from tensor shapes):
  Input  : 29 features
  Layer 0: Linear(29 → 128) + BatchNorm1d(128) + ReLU + Dropout(0.3)   [network.0, network.1]
  Layer 1: Linear(128 → 64) + BatchNorm1d(64)  + ReLU + Dropout(0.3)   [network.4, network.5]
  Layer 2: Linear(64 → 5)                                                [network.8]

Output classes (from target_label_encoder.pkl):
  0 → Data Exfiltration
  1 → IT Sabotage
  2 → Intellectual Property Theft
  3 → Normal
  4 → Unauthorized Access
"""
import torch
import torch.nn as nn


class BehavioralIntelligenceNet(nn.Module):
    """
    Deep neural network for insider threat classification.
    Trained on CERT r4.2 behavioral features.
    """

    INPUT_DIM  = 29   # number of engineered features (matches scaler)
    HIDDEN1    = 128
    HIDDEN2    = 64
    N_CLASSES  = 5    # matches label encoder classes
    DROPOUT    = 0.3

    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            # Block 1: Linear → BatchNorm → ReLU → Dropout
            nn.Linear(self.INPUT_DIM, self.HIDDEN1),      # network.0
            nn.BatchNorm1d(self.HIDDEN1),                  # network.1
            nn.ReLU(),                                     # network.2
            nn.Dropout(self.DROPOUT),                      # network.3

            # Block 2: Linear → BatchNorm → ReLU → Dropout
            nn.Linear(self.HIDDEN1, self.HIDDEN2),         # network.4
            nn.BatchNorm1d(self.HIDDEN2),                  # network.5
            nn.ReLU(),                                     # network.6
            nn.Dropout(self.DROPOUT),                      # network.7

            # Output
            nn.Linear(self.HIDDEN2, self.N_CLASSES),       # network.8
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Return softmax probabilities."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            return torch.softmax(logits, dim=1)

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Return class index predictions."""
        return self.predict_proba(x).argmax(dim=1)
