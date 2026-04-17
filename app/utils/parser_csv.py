import io
import polars as pl

def manipulate_data(return_text_ia):
    df = pl.read_csv(
        io.StringIO(return_text_ia),
        separator=';'
    )

    df.write_csv(
        'files.csv',
        separator=';'
    )

