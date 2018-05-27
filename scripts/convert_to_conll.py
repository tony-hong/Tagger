# convert_to_conll.py
# author: Playinf
# email: playinf@stu.xmu.edu.cn

import re
import os
import sys


def convert_bio(labels):
    n = len(labels)
    tags = []

    tag = []
    count = 0

    # B I*
    for label in labels:
        count += 1

        if count == n:
            next_l = None
        else:
            next_l = labels[count]

        if label == "O":
            if tag:
                tags.append(tag)
                tag = []
            tags.append([label])
            continue

        tag.append(label[2:])

        if not next_l or next_l[0] == "B":
            tags.append(tag)
            tag = []

    new_tag = []

    for tag in tags:
        if len(tag) == 1:
            if tag[0] == "O":
                new_tag.append("*")
            else:
                new_tag.append("(" + tag[0] + "*)")
            continue

        label = tag[0]
        n = len(tag)

        for i in range(n):
            if i == 0:
                new_tag.append("(" + label + "*")
            elif i == n - 1:
                new_tag.append("*)")
            else:
                new_tag.append("*")

    return new_tag


def print_sentence_to_conll(fout, tokens, labels):
    for label_column in labels:
        assert len(label_column) == len(tokens)
    for i in range(len(tokens)):
        fout.write(tokens[i].ljust(15))
        for label_column in labels:
            fout.write(label_column[i].rjust(15))
        fout.write("\n")
    fout.write("\n")


def print_to_conll(pred_labels, gold_props_file, output_filename):
    fout = open(output_filename, 'w')
    seq_ptr = 0
    num_props_for_sentence = 0
    tokens_buf = []

    for line in open(gold_props_file, 'r'):
        line = line.strip()
        if line == "" and len(tokens_buf) > 0:
            print_sentence_to_conll(
                fout,
                tokens_buf,
                pred_labels[seq_ptr:seq_ptr+num_props_for_sentence]
            )
            seq_ptr += num_props_for_sentence
            tokens_buf = []
            num_props_for_sentence = 0
        else:
            info = line.split()
            num_props_for_sentence = len(info) - 1
            tokens_buf.append(info[0])

    # Output last sentence.
    if len(tokens_buf) > 0:
        print_sentence_to_conll(
            fout,
            tokens_buf,
            pred_labels[seq_ptr:seq_ptr+num_props_for_sentence]
        )

    fout.close()


if __name__ == "__main__":
    '''
    Args:
        | *1* (fn) -- path to all decodes files 
        | *2* (fn) -- path to all propid files
        | *3* (dir) -- output dir
    '''
    decode_fns = [os.path.join(sys.argv[1], name) for name in os.listdir(sys.argv[1]) if re.search(r'decodes', name)]
    propid_fns = [os.path.join(sys.argv[2], name) for name in os.listdir(sys.argv[2]) if re.search(r'props', name)]
    
    print decode_fns
    print propid_fns
    for i, decode_fn in enumerate(decode_fns):
        propid_fn = propid_fns[i]
        output_name = re.findall(r'split/(.*)_pred', propid_fn)[-1]
        output_name += '_srl.conll'
        output_fn = os.path.join(sys.argv[3], output_name)
        print output_name
        print output_fn

        all_labels = []
        with open(decode_fn, 'r') as fd:
            for text_line in fd:
                labs = text_line.strip().split()
                labs = convert_bio(labs)
                all_labels.append(labs)

        # print all_labels
        print 'Processing ...'
        print_to_conll(all_labels, propid_fn, output_fn)
        print 'Done !'
