# TCPSendPicture

Method 380

This method is used to transmit a picture represented by a [Bitmap](../objects/bitmap.md) object to a TCP/IP socket. The picture may be transmitted in GIF or in PNG format.

The argument to TCPSendPicture is a 1 or 2-element array as follows:

|-----|--------------|------------------------------------|
|`[1]`|Bitmap name   |character vector                    |
|`[2]`|Picture format|character vector, `'GIF'` or `'PNG'`|

If *Picture format* is omitted, the default is GIF format.

The [Style](../properties/style.md) of the [TCPSocket](../objects/tcpsocket.md) object must be set to `'Raw'` before you execute the TCPSendPicture method.

The ([shy](../../programming-reference-guide/introduction/results.md#shy-results)) result of the method is an integer that reports the number of bytes that were transmitted.

## Example
```apl
      S1.TCPSendPicture 'BM' 'PNG'        
4930
```

See also: [MakeGIF](./makegif.md), [MakePNG](./makepng.md)

## Application

Objects: [TCPSocket](../objects/tcpsocket.md)
