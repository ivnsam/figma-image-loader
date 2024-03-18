# Figma image loader

## About
This is script for download objects(nodes) with enabled export as image from Figma.
It can be used in automation tasks for downloading images or icons from Figma.

Made using [Phind](https://www.phind.com/) by [Ivan Samoylenko](https://www.linkedin.com/in/ivnsam).

[Figma API documentation](https://www.figma.com/developers/api#get-images-endpoint).


## How to use
- [Create](https://help.figma.com/hc/en-us/articles/8085703771159-Manage-personal-access-tokens) your Figma personal access token - `TOKEN` in command below
- Import download_test.fig into your Figma account or enable export for needed items in your Figma file
- Find and write down ID of imported file ([where to find ID](https://iconify.design/docs/libraries/tools/import/figma/file-id.html)) - `FILE_ID` in command below
- Run python script with command below
    ```bash
    python3 main.py [-h] -t TOKEN -f FILE_ID -p OUTPUT_DIR [--format FORMAT -l LOGLEVEL]
    ```
    here:
    - `-t/--token TOKEN` and `-f/--file FILE_ID` - from previous steps
    - `-p/--path OUTPUT_DIR` - name of directory where to save output images (it can be relative path too), directory will be created automatically
    - `--format FORMAT` - can be jpg, png, svg, or pdf; default: svg ([about formats in Figma documentation](https://www.figma.com/developers/api#get-images-endpoint:~:text=image%20scaling%20factor-,format,-Stringoptional))
    - `-l/--loglevel LOGLEVEL` - can be DEBUG, INFO, WARNING, ERROR or CRITICAL; default: INFO


## How it works
- Creates output directory if it doesn't exist
- Retrieves all nodes for file with FILE_ID from the Figma API
- Selects nodes with enabled “export” parameter
- Obtains URL to image file from the Figma API
- Downloads image file by url
