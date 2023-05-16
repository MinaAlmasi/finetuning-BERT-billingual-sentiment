'''
Fine-tuning BERT for bilingual emotion classification in English and Spanish

# https://huggingface.co/docs/transformers/v4.17.0/en/tasks/sequence_classification#finetune-with-trainer
'''

# utils 
import pathlib 
import argparse

# to define parameters for model 
from transformers import TrainingArguments

# custom moduels
from finetune_fns import finetune
from data_fns import load_datasets
from plot_fns import get_loss

def input_parse():
    parser = argparse.ArgumentParser()

    # add arguments 
    parser.add_argument("-hub", "--push_to_hub", help = "Whether to push to huggingface hub or not", type = bool, default = False) #default img defined
    
    # save arguments to be parsed from the CLI
    args = parser.parse_args()

    return args

def main(): 
    # intialise args 
    args = input_parse()

    # define model outpath
    path = pathlib.Path(__file__)
    modeloutpath = path.parents[1] / "models"
    modeloutpath.mkdir(exist_ok=True)

    path = pathlib.Path(__file__)
    tass_path = path.parents[1] / "data"

    ds, ds_overview = load_datasets(tass_path)

    # map labels to ids
    id2label = {0: "negative", 1:"neutral", 2:"positive"}
    label2id = {"negative":0, "neutral":1, "positive":2}

    # define training arguments 
    training_args = TrainingArguments(
        output_dir = modeloutpath, 
        push_to_hub = args.push_to_hub,
        learning_rate=2e-5,
        per_device_train_batch_size = 16, 
        per_device_eval_batch_size = 16, 
        num_train_epochs=1, 
        weight_decay=0.01,
        evaluation_strategy="epoch", 
        save_strategy = "epoch", 
        load_best_model_at_end = True
    )

    trainer = finetune(
        dataset = ds, 
        model_name = "bert-base-multilingual-cased", 
        n_labels = 3,
        id2label = id2label,
        label2id = label2id,
        training_args = training_args
        )

    loss = get_loss(trainer.state.log_history)
    print(loss)


    if args.push_to_hub == True: 
        from huggingface_hub import login

        # get token from txt
        with open(path.parents[1] / "token.txt") as f:
            hf_token = f.read()

        login(hf_token)


if __name__ == "__main__":
    main()