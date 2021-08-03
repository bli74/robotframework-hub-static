*** Variables ***
| ${docu_dir} | tests/_docu

*** Settings ***
| Library | OperatingSystem

*** Test Cases ***
| Run with 0 arguments
| | [Documentation]
| | ... | keyword_doc fails and prints usage without parameters
| | ${rc} | ${output} | Run And Return Rc And Output | keyword_doc
| | Should Not Be Equal As Integers | 0 | ${rc}
| | Should Start With | ${output} | Usage:

| Run with 1 argument
| | [Documentation]
| | ... | keyword_doc fails and prints usage with one parameters
| | ${rc} | ${output} | Run And Return Rc And Output | keyword_doc tests/sample_resources
| | Should Not Be Equal As Integers | 0 | ${rc}
| | Should Start With | ${output} | Usage:

| Run with correct arguments
| | [Documentation]
| | ... | keyword_doc creates index.html and library documentation
| | ${rc} | ${output} | Run And Return Rc And Output | keyword_doc tests/sample_resources ${docu_dir}
| | Should Be Equal As Integers | 0 | ${rc}
| | File Should Exist | ${docu_dir}${/}index.html
| | File Should Exist | ${docu_dir}${/}BuiltIn.html
| | File Should Exist | ${docu_dir}${/}eb_keyword${/}ContextHandler.html
