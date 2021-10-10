# BSV-block-txs-origin

> Check the percentage of known opReturn origins of all transactions in a BSV mainnet block.

## Expected output

```
None: 26%
OP_RETURN: 10%
metanet: 22%
bitcom: 19%
run: 23%
```
## About the code
This script uses the WhatsOnChain [API](https://developers.whatsonchain.com/#rate-limits) to get the on Chain data.

## Use 

1. Clone or download repo
2. Run the ``main.py``
3. Give the blockheight of the block you want to check
   >  [Block](https://whatsonchain.com/block/00000000000000000bc2e6618c47ec9bba05b33be4c5699cfe10c8b8aa139783) ``708354``
4. Wait for results...

## Future 🔮
- Add total for known big uploaders, like **cryptofights.io**, **moneybutton.com**, **peergame.com** etc.

## Author
Made with :heart: by [antmaster2001](https://github.com/antmaster2001)