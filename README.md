##    Developed and tested on:

conda 4.3.22 (Python 3.6)

numpy==1.16.3
scikit-learn==0.19.1


##    Run tests 

```sh
pytest test.py -v
```


##    Run on user specified maximum line length and number of lines

```sh
python run.py --n_lines=10 --max_line_length=97
``` 


##    Run on user specified (not generated) file 

```sh
python run.py --generate='n' --file='test.txt'
```


