import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader

# =====================================================================
# 1. LOAD DATASETS
# =====================================================================
print("Loading CERT datasets...")
logon_data = pd.read_csv('/kaggle/input/cert-insider-threat-detection-research/logon.csv')
email_data = pd.read_csv('/kaggle/input/cert-insider-threat-detection-research/email.csv')
file_data = pd.read_csv('/kaggle/input/cert-insider-threat-detection-research/file.csv')
device_data = pd.read_csv('/kaggle/input/cert-insider-threat-detection-research/device.csv')
psychometric_data = pd.read_csv('/kaggle/input/cert-insider-threat-detection-research/psychometric.csv')
http_data = pd.read_csv('/kaggle/input/cert-insider-threat-detection-research/http.csv', nrows=3000000)

# =====================================================================
# 2. CORE FEATURE SPACE GENERATION
# =====================================================================
print("Extracting behavioral analytics features...")

# Logon Feature Engineering
logon_data['date'] = pd.to_datetime(logon_data['date'])
logon_data['day'] = logon_data['date'].dt.dayofweek 
logon_data['hour'] = logon_data['date'].dt.hour

logon_features = logon_data.groupby('user').agg(
    L1=('pc', 'nunique'),
    L2=('activity', lambda x: (x == 'Logon').sum()),
    L3=('activity', lambda x: (x == 'Logoff').sum()),
    L6=('day', lambda x: (x >= 5).sum()),
    L7=('day', lambda x: (x < 5).sum()),
    L8=('pc', lambda x: x.value_counts().idxmax() if not x.empty else 'Unknown'),
    L9=('hour', lambda x: ((x < 6) | (x > 18)).sum()),
    L10=('hour', lambda x: ((x >= 6) & (x <= 18)).sum()),
).reset_index()

# Email Feature Engineering
email_data['date'] = pd.to_datetime(email_data['date'])
email_data['hour'] = email_data['date'].dt.hour
email_data['attachments'] = pd.to_numeric(email_data['attachments'], errors='coerce').fillna(0).astype(int)

email_features = email_data.groupby('user').agg(
    E1=('to', 'nunique'),
    E4=('size', 'mean'),
    E6=('to', lambda x: sum('@' in str(addr) and not str(addr).endswith('dtaa.com') for addr in x.astype(str))),
    E10=('to', lambda x: x.value_counts().idxmax() if not x.empty else 'Unknown'),
    E11=('size', 'sum'),
).reset_index()

# HTTP Feature Engineering
http_data['date'] = pd.to_datetime(http_data['date'])
http_data['day'] = http_data['date'].dt.dayofweek 

http_features = http_data.groupby('user').agg(
    H1=('url', 'nunique'),
    H2=('activity', 'count'),
    H5=('activity', lambda x: x.str.contains('WWW Upload', case=False, na=False).sum()),
    H9=('url', lambda x: x.str.len().mean()),
).reset_index()

# File Activity Engineering
file_data['date'] = pd.to_datetime(file_data['date'])
file_data['to_removable_media'] = file_data['to_removable_media'].astype(bool)

file_features = file_data.groupby('user').agg(
    F1=('filename', 'nunique'),
    F3=('to_removable_media', 'sum'),
    F7=('activity', lambda x: x.str.contains('delete', case=False, na=False).sum()),
    F8=('activity', lambda x: x.str.contains('copy', case=False, na=False).sum()),
).reset_index()

# Device Feature Engineering
device_data['date'] = pd.to_datetime(device_data['date'])
device_data['hour'] = device_data['date'].dt.hour

device_features = device_data.groupby('user').agg(
    D2=('activity', 'count'),
    D3=('hour', lambda x: ((x < 6) | (x > 18)).sum()),
    D6=('activity', lambda x: x.str.contains('disconnect', case=False, na=False).sum()),
).reset_index()

# Psychometric Alignment
psychometric_features = psychometric_data[['user_id', 'O', 'C', 'E', 'A', 'N']].copy()
psychometric_features.rename(columns={"user_id": "user"}, inplace=True)

# =====================================================================
# 3. MERGE & BASELINE CLASSIFICATION LABELS
# =====================================================================
print("Merging structural matrices...")
combined_df = logon_features
for df in [email_features, http_features, file_features, device_features, psychometric_features]:
    combined_df = combined_df.merge(df, on='user', how='outer')

# Standard Fill For Inferred Absolute Zeros
na_zeros = ['F1', 'F3', 'F7', 'F8', 'D2', 'D3', 'D6', 'H5']
combined_df[na_zeros] = combined_df[na_zeros].fillna(0)

# Calculating baseline organizational metrics
feature_columns = ['F8', 'D3', 'F7', 'D6', 'H5', 'L9', 'F3', 'E6']
feature_means = combined_df[feature_columns].mean()

def assign_label(row):
    if all(row[feature] <= feature_means[feature] * 0.9 for feature in feature_columns):
        return "Normal"
    elif row['F8'] > feature_means['F8'] * 1.2 or row['D3'] > feature_means['D3'] * 1.2:
        return "Intellectual Property Theft"
    elif row['F7'] > feature_means['F7'] * 1.2 or row['D6'] > feature_means['D6'] * 1.2:
        return "IT Sabotage"
    elif row['H5'] > feature_means['H5'] * 1.2 or row['L9'] > feature_means['L9'] * 1.2:
        return "Unauthorized Access"
    elif row['F3'] > feature_means['F3'] * 1.2 or row['E6'] > feature_means['E6'] * 1.2:
        return "Data Exfiltration"
    else:
        return "Normal"

print("Assigning deterministic behavioral target vectors...")
combined_df['Label'] = combined_df.apply(assign_label, axis=1)

# Clean Identifiers out of structural spaces
X = combined_df.drop(columns=['user', 'Label'], errors='ignore')
y = combined_df['Label']

# Encoding Matrix Categoricals
categorical_cols = X.select_dtypes(include=['object']).columns
for col in categorical_cols:
    le_cat = LabelEncoder()
    X[col] = le_cat.fit_transform(X[col].astype(str))

# Median Imputation strategy for explicit missing fields
X.fillna(X.median(), inplace=True)

# Save the encoder for target mappings
target_encoder = LabelEncoder()
y_encoded = target_encoder.fit_transform(y)
class_mappings = dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))
print("Class targets finalized: ", class_mappings)

# Standard scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# =====================================================================
# 4. DEEP LEARNING SPLITS & DATALOADERS
# =====================================================================
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, stratify=y_encoded, random_state=42
)

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

train_loader = DataLoader(TensorDataset(X_train_tensor, y_train_tensor), batch_size=64, shuffle=True)
test_loader = DataLoader(TensorDataset(X_test_tensor, y_test_tensor), batch_size=64)

# =====================================================================
# 5. CORE DEEP BEHAVIORAL ANALYTICS MODEL (MLP)
# =====================================================================
class BehavioralIntelligenceMLP(nn.Module):
    def __init__(self, input_dim, num_classes=5):
        super(BehavioralIntelligenceMLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x):
        return self.network(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = BehavioralIntelligenceMLP(input_dim=X_train.shape[1], num_classes=len(class_mappings)).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

# =====================================================================
# 6. MODEL TRAINING
# =====================================================================
epochs = 30
train_losses, val_losses = [], []

print(f"Starting pipeline convergence across {epochs} epochs on device: {device}...")
for epoch in range(epochs):
    model.train()
    total_train_loss = 0
    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        
        total_train_loss += loss.item()
        
    # Evaluation Cycle
    model.eval()
    total_val_loss = 0
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            total_val_loss += loss.item()
            
    train_losses.append(total_train_loss / len(train_loader))
    val_losses.append(total_val_loss / len(test_loader))
    
    if (epoch + 1) % 5 == 0 or epoch == 0:
        print(f"Epoch {epoch+1:02d}/{epochs} | Train Loss: {train_losses[-1]:.4f} | Val Loss: {val_losses[-1]:.4f}")

# Plot performance curves
plt.figure(figsize=(8, 5))
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Validation Loss', linestyle='--')
plt.title('Pipeline Baseline Loss Convergence')
plt.xlabel('Epochs')
plt.ylabel('Loss Value')
plt.legend()
plt.grid(True)
plt.show()

# =====================================================================
# 7. PERFORMANCE VALDIATION
# =====================================================================
model.eval()
all_preds = []
all_targets = []
with torch.no_grad():
    for batch_x, batch_y in test_loader:
        batch_x = batch_x.to(device)
        logits = model(batch_x)
        preds = torch.argmax(logits, dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_targets.extend(batch_y.numpy())

print("\n--- Pipeline Evaluation Metrics ---")
print(classification_report(all_targets, all_preds, target_names=target_encoder.classes_))

# =====================================================================
# 8. EXPORT AND DOWNLOAD SYSTEM MODEL
# =====================================================================
print("Serializing baseline structural tracking objects...")

# Export processing scaler states
joblib.dump(scaler, 'pipeline_scaler.pkl')
joblib.dump(target_encoder, 'target_label_encoder.pkl')

# Save model parameters
MODEL_PATH = 'behavioral_intelligence_model.pth'
torch.save(model.state_dict(), MODEL_PATH)
print(f"Model parameters successfully generated and saved to: {MODEL_PATH}")

# Code snippet generation allowing immediate downloading in web notebook environments
try:
    from IPython.display import FileLink
    print("\nClick the links below to download your trained model components:")
    display(FileLink('behavioral_intelligence_model.pth'))
    display(FileLink('pipeline_scaler.pkl'))
except ImportError:
    print("\nFile link generation skipped. Access trained model artifacts via your local workspace.")
