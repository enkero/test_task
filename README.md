##    Developed and tested on:

conda 4.3.22 (Python 3.6)

numpy==1.16.3

scikit-learn==0.19.1

pytest==3.0.5


##    Run tests 

```sh
pytest test.py -v
```


##    See example of test file and result 

test.txt - generated file

sorted.txt - sorted file


##    Run on user specified maximum line length, number of lines and maximum size of read text per batch (in Gb)

```sh
python run.py --n_lines=10 --max_line_length=97 --gb 1.0
``` 


##    Run on user specified (not generated) file 

```sh
python run.py --generate='n' --file='test.txt' --gb 1.0
```