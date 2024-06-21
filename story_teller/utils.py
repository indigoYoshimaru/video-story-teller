from typing import Text


def read_env(env_file: Text):
    from dotenv import dotenv_values
    env_dict = dotenv_values(env_file)
    return env_dict


from typing import Text, Dict, Any, Union, List, Generator
from pydantic import BaseModel, Field

# from gcsfs import GCSFileSystem as GCSFS
from fs_gcsfs import GCSFS
import pandas as pd
from fs.osfs import OSFS
from loguru import logger


class ReaderWriterConfig(BaseModel):
    logging_level: Union[Text, int] = "INFO"
    large_file_chunking: bool = False
    chunksize: int = 20
    json_indent: int = 4


class ReaderWriterBase(BaseModel):
    fs: Union[GCSFS, OSFS] = Field(default=None)
    mapper: Dict = Field(default=None)
    logger: Any = Field(default=None)
    config: ReaderWriterConfig = Field(default=None)

    def __init__(
        self,
        config: ReaderWriterConfig = None,
        fs: GCSFS = None,
        mapper: Dict = None,
        root_path: Text = "", 
    ):

        msg = f"Init with config {config}"
        if not config:
            config = ReaderWriterConfig()
            msg = "Using default config"

        logger.info(f"{msg}")
        if not fs:
            logger.info("No GCSFS provided. Using OS filesystem.")
            fs = OSFS(root_path=root_path)
            
        super().__init__(
            fs=fs,
            logger=logger,
            mapper=mapper,
            config=config,
        )

    class Config:
        arbitrary_types_allowed = True


class FileReader(ReaderWriterBase):
    def __init__(self, cfg: ReaderWriterConfig = None, fs: GCSFS = None):
        mapper = dict(
            csv=self.read_df,
            xlsx=self.read_df,
            json=self.read_json,
            yaml=self.read_yaml,
        )

        super().__init__(
            fs=fs,
            mapper=mapper,
            config=cfg,
        )

    def get_available_file(self, file_dir: Text):
        return self.fs.listdir(file_dir)

    def read(self, file_path: Text) -> Union[Generator, List, Dict, pd.DataFrame]:
        try:
            assert file_path, "Empty file path"
            try:
                extension = file_path.split(".")[-1]
                assert (
                    extension in self.mapper
                ), "Extension {extension} is not implemented"
            except Exception as e:
                raise NotImplementedError(e)
            self.logger.info(f"Reading {extension} file from path {file_path}")
            result = self.mapper[extension](file_path)
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            raise e
        else:
            self.logger.success(
                f"large_file_chunking is {self.config.large_file_chunking}. Output format has type: {type(result)}"
            )
            return result

    def read_json(self, file_path: Text) -> Union[List, Dict]:
        import json

        with self.fs.open(file_path) as f:
            output = json.load(f)
        return output

    def read_yaml(self, file_path: Text) -> Union[List, Dict]:
        import yaml

        with self.fs.open(file_path) as f:
            output = yaml.full_load(f)
        return output

    def read_df(self, file_path: Text):
        function_by_format = dict(
            csv=pd.read_csv,
            xlsx=pd.read_excel,
        )
        func = function_by_format[file_path.split(".")[-1]]
        with self.fs.open(file_path) as f:
            if not self.config.large_file_chunking:
                return func(f)
            for chunk in func(f, chunksize=self.config.chunksize):
                yield chunk


class FileWriter(ReaderWriterBase):
    def __init__(self, cfg: ReaderWriterConfig = None, fs: GCSFS = None):
        mapper = dict(
            csv=self.write_df,
            xlsx=self.write_df,
            json=self.write_json,
            yaml=self.write_yaml,
        )

        super().__init__(
            fs=fs,
            mapper=mapper,
            config=cfg,
        )

    def write(
        self,
        file_path: Text,
        content: Union[List, Dict, pd.DataFrame],
        header: List = [],
        mode: Text = "w",
    ) -> None:
        try:
            assert file_path, "Empty file path"
            assert any(content), "No content to write"
            try:
                extension = file_path.split(".")[-1]
                assert (
                    extension in self.mapper
                ), "Extension {extension} is not implemented"
            except Exception as e:
                raise NotImplementedError(e)

            self.check_available_path(file_path)
            self.logger.info(f"Writing with {extension} to {file_path}")
            self.mapper[extension](
                file_path,
                content,
                header,
                mode,
            )
        except Exception as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            raise e
        else:
            self.logger.success(f"Data has been written to {file_path}")

    def write_json(
        self,
        file_path: Text,
        content: Union[Dict, List],
        header: List,
        mode: Text,
    ):
        import json

        with self.fs.open(file_path, mode, encoding="utf8") as f:
            f.write(
                json.dumps(
                    content,
                    indent=self.config.json_indent,
                    ensure_ascii=False,
                )
            )

    def write_yaml(
        self,
        file_path: Text,
        content: Union[Dict, List],
        header: List,
        mode: Text,
    ):
        import yaml

        with self.fs.open(file_path, mode, encoding="utf8") as f:
            yaml.dump(
                content,
                f,
                default_flow_style=False,
                allow_unicode=True,
            )

    def write_df(
        self,
        file_path: Text,
        content: Union[Dict, pd.DataFrame],
        header: List,
        mode: Text,
    ):
        function_by_format = dict(
            csv=content.to_csv,
            xlsx=content.to_excel,
        )

        func = function_by_format[file_path.split(".")[-1]]

        if type(self.fs) == OSFS:
            from os import path as fs
        else:
            fs = self.fs
            fs.fix_storage()

        if fs.exists(file_path):
            self.logger.info(f"No writing header")
            with self.fs.open(file_path, mode) as f:
                func(f, mode=mode, header=False)
            return

        with self.fs.open(file_path, mode) as f:
            func(f, mode=mode, header=header)

    def check_available_path(self, file_path: Text):
        directory = file_path.rsplit("/", 1)[0]
        if not self.fs.exists(directory):
            self.logger.warning(
                f"Directory {directory} does not exist! Making directory..."
            )
            self.fs.makedirs(directory)