#!/use/bin/python3

import os

from configFileStoreClientFactory import configFileStoreClientFactory

def runTestCase (testcaseID:str, clientID:str, host:str, port:int, verbose:int=0) -> bool:
    print (f"[{testcaseID}] Start execution...")
    import tempfile
    import lorem
    import hashlib

    ############################################
    # Prepare inputs
    ############################################
    tmpdir = tempfile.TemporaryDirectory (prefix="configFileStoreClient", dir="/tmp")
    infile = os.path.join (tmpdir.name, "infile.txt")
    outfile = os.path.join (tmpdir.name, "outfile.txt")

    with open(infile, "w") as f:
        f.write (lorem.sentence())
        f.write (lorem.paragraph())
        f.write (lorem.text())

    ############################################
    # Execute test
    ############################################
    factory = configFileStoreClientFactory ()

    # Default values for all arguments
    client = factory.getClient(clientID)
    if not client:
        print (f"[{testcaseID}] Failed to get client")
        return False

    if not client.init(host, port):
        print (f"[{testcaseID}] Client init failed")
        return False

    if not client.push ("uniquekey", infile):
        print (f"[{testcaseID}] push failed")
        return False

    if not client.pull ("uniquekey", outfile):
        print (f"[{testcaseID}] pull failed")
        return False

    ############################################
    # Check results
    ############################################
    with open (infile,"r") as f:
        indata = f.read()
        infilehash = hashlib.md5(indata.encode('utf-8')).hexdigest()

    with open (outfile,"r") as f:
        outdata = f.read()
        outfilehash = hashlib.md5(outdata.encode('utf-8')).hexdigest()

    ############################################
    # Log results
    ############################################
    if verbose >= 2:
        print (f"[{testcaseID}] In file data ---------------------")
        print (indata)
        print (f"[{testcaseID}] Out file data ---------------------")
        print (outdata)

    if verbose == 1:
        print (f"[{testcaseID}] In file data hash ---------------------")
        print (infilehash)
        print (f"[{testcaseID}] Out file data hash ---------------------")
        print (outfilehash)

    if infilehash == outfilehash:
        print (f"[{testcaseID}] Test successful (hash matches)")
    else:
        print (f"[{testcaseID}] Test failed (hash mismatch)")

    return True


#######################################
# Test Cases
#######################################
if __name__ == "__main__":
    # Default values
    runTestCase ("tc_001", None, None, None, 0)

    # Positive test case
    runTestCase ("tc_002", "redis", "127.0.0.1", 6379, 0)

    # Negative test case
    runTestCase ("tc_003", "redis", "127.0.0.1", 6666, 0)
    runTestCase ("tc_004", "redis", "123.456.789.101", 6666, 0)
