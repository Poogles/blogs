# Blocking asyncio with sync calls.

To setup...

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host=0.0.0.0
```

To check async...

```sh
./test.sh async
using async
"fast\n"
"async slow\n"
done
```

As expected the fast call returns before the slow.


```sh
./test.sh sync
using sync
"sync slow\n""fast\n"

done
```

Ruh roh, our fast call is arriving after the slow. The API has not
been able to service our request as it's been blocked.
