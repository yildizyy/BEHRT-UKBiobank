import pandas as pd
import numpy as np
import pickle
import simple_icd_10 as icd
import os
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, average_precision_score

# --- SETTINGS ---
tasks_config = {
    "Task 1 (Next Visit)": {"suffix": "task1", "output_name": "Revised_Table_S1_Task1.csv"},
    "Task 2 (6 Months)":   {"suffix": "task2", "output_name": "Revised_Table_S2_Task2.csv"},
    "Task 3 (12 Months)":  {"suffix": "task3", "output_name": "Revised_Table_S3_Task3.csv"},
    "Task 4 (5 Years)":    {"suffix": "task4", "output_name": "Revised_Table_S4_Task4.csv"}
}

IGNORED_TOKENS = {'NONE', 'UNK', '[UNK]', 'SEP', '[SEP]', 'CLS', '[CLS]', 'PAD', '[PAD]', 'MASK', '[MASK]'}

def get_icd_name(code):
    try:
        clean = str(code).replace('.', '')
        desc = icd.get_description(clean)
        return desc if desc else "Description Not Found"
    except:
        return "Description Not Found"

def get_optimal_threshold_and_metrics(y_true, y_probs):
    """
Finds the 'Optimal Threshold' for each disease. Selects the point that maximizes the F1 Score.
    """
    precision, recall, thresholds = precision_recall_curve(y_true, y_probs)
    
    # Calculate F1 Score: 2 * (P * R) / (P + R)
    fscore = (2 * precision * recall) / (precision + recall + 1e-10)
    
    # max F1
    ix = np.argmax(fscore)
    best_thresh = thresholds[ix]
    best_f1 = fscore[ix]
    
    
    best_prec = precision[ix]
    best_rec = recall[ix]
    
    return best_thresh, best_prec, best_rec, best_f1

def analyze_task_advanced(task_name, config):
    suffix = config["suffix"]
    print(f"\n{'='*60}")
    print(f"{task_name}")
    
    pred_path = f"y_pred_{suffix}.npy"
    true_path = f"y_true_{suffix}.npy"
    vocab_path = f"label_vocab_{suffix}.pkl"
    
    if not (os.path.exists(pred_path) and os.path.exists(true_path)):
        print("wrong path")
        return None

    
    
    y_logits = np.load(pred_path)
    y_true = np.load(true_path)
    with open(vocab_path, 'rb') as f:
        label_vocab = pickle.load(f)
    
    idx2code = {v: k for k, v in label_vocab.items()}
    
    #(Sigmoid)
    y_probs = 1 / (1 + np.exp(-y_logits))
    
    #frequencies
    disease_frequencies = np.sum(y_true, axis=0)
    sorted_indices = np.argsort(disease_frequencies)[::-1]
    
    table_data = []
    rank_counter = 1
    
    
    
    for idx in sorted_indices:
        code = idx2code[idx]
        count = disease_frequencies[idx]
        
        if code in IGNORED_TOKENS or count == 0:
            continue
        if rank_counter > 20:
            break
        
        
        true_col = y_true[:, idx]
        prob_col = y_probs[:, idx]
        
        # auroc
        try:
            auroc = roc_auc_score(true_col, prob_col)
        except:
            auroc = 0.5 
            
        # APS
        aps = average_precision_score(true_col, prob_col)
        
         
        # OPTIMAL THRESHOLD
        best_thresh, best_prec, best_rec, best_f1 = get_optimal_threshold_and_metrics(true_col, prob_col)
        
        table_data.append({
            "Rank": rank_counter,
            "Code": code,
            "Disease Name": get_icd_name(code),
            "N": int(count),
            "AUROC": round(auroc, 3),        
            "APS": round(aps, 3),            
            "Opt. Thresh": round(best_thresh, 4), 
            "Adj. Recall": round(best_rec, 3),    
            "Adj. Precision": round(best_prec, 3) 
        })
        
        rank_counter += 1
        
    df_result = pd.DataFrame(table_data)
    df_result.to_csv(config["output_name"], index=False)
    print(df_result.head())
    
    return df_result


for task, conf in tasks_config.items():
    analyze_task_advanced(task, conf)
