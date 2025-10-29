import type { Socket } from "socket.io-client";

class multipleFileUpload {
  private files: File[];
  private totalSlice: number;
  private sliceSize: number = 1024 * 1024;
  private currentSlice: number = 0;
  private fileSocket: Socket;

  constructor(files: File[]) {
    // randomly picked 1MB slices,
    // I don't think this size is important for this experiment
    this.totalSlice = 0;
    this.files = files;
    this.files.forEach((file) => {
      this.totalSlice = Math.ceil(file.size / (1024 * 1024));
    });

    this.fileSocket = socketio.socket("/files");
  }

  private slices(file: File) {
    return Math.ceil(file.size / this.sliceSize);
  }
  private getNextSlice(file: File) {
    var start = this.currentSlice * this.sliceSize;
    var end = Math.min((this.currentSlice + 1) * this.sliceSize, file.size);
    ++this.currentSlice;

    return file.slice(start, end);
  }

  public async uploadFiles() {
    this.fileSocket.connect();
    this.files.forEach((file) => {
      this.currentSlice = 0;
      this.totalSlice = Math.ceil(file.size / (1024 * 1024));
      for (let i = 0; i < this.slices(file); i++) {
        this.fileSocket.emit("add_file", { name: file.name, chunk: this.getNextSlice(file) });
      }
    });
  }
}

export default multipleFileUpload;
