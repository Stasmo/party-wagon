class PartyWagon {

  commandChar = '§';

  bluefruit = {
    serviceUUID: "6e400001-b5a3-f393-e0a9-e50e24dcca9e",
    txCharacteristic: "6e400002-b5a3-f393-e0a9-e50e24dcca9e",
    rxCharacteristic: "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
  }

  service = null
  readCharacteristic = null
  writeCharacteristic = null
  connected = false

  constructor() {
    this.device = null;
    this.onDisconnected = this.onDisconnected.bind(this);
    this.onMessage = this.onMessage.bind(this);
  }

  stringToBytes(string) {
    var array = new Uint8Array(string.length);
    for (var i = 0, l = string.length; i < l; i++) {
      array[i] = string.charCodeAt(i);
    }
    return array.buffer;
  }

  bytesToString(buffer) {
    return String.fromCharCode.apply(null, new Uint8Array(buffer));
  }

  request() {
    let options = {
      "filters": [{
        "name": "Party Wagon"
      }],
      "optionalServices": [
        this.bluefruit.serviceUUID
      ]
    };

    return navigator.bluetooth.requestDevice(options)
    .then(device => {
      this.device = device;
      this.device.addEventListener('gattserverdisconnected', this.onDisconnected);
    });
  }

  async connect() {
    if (!this.device) {
      throw Error('Device is not connected.');
    }

    try {
      const server = await this.device.gatt.connect();
      this.service = await server.getPrimaryService(this.bluefruit.serviceUUID)
      this.readCharacteristic = await this.service.getCharacteristic(this.bluefruit.rxCharacteristic);
      this.writeCharacteristic = await this.service.getCharacteristic(this.bluefruit.txCharacteristic);
      this.readCharacteristic.startNotifications();
      this.readCharacteristic.addEventListener('characteristicvaluechanged', this.onMessage);
      this.connected = true;
    } catch(e) {
      console.error(e);
    }
  }

  setDirection(dir) {
    this.writeLine([this.commandChar, 'dir', dir].join(':'));
  }

  writeLine(data) {
    return this.writeCharacteristic.writeValue(this.stringToBytes(data));
  }

  disconnect() {
    if (!this.device) {
      return Promise.reject('Device is not connected.');
    }
    return this.device.gatt.disconnect();
  }

  onDisconnected() {
    console.log('Device is disconnected.');
    this.service = null;
    this.readCharacteristic = null;
    this.writeCharacteristic = null;
    this.connected = false;
  }

  onMessage(event) {
    const value = event.target.value;
    const decoded = this.bytesToString(value.buffer);
    console.log(value, decoded)
  }
}

export default PartyWagon;