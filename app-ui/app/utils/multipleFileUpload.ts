import type { Socket } from "socket.io-client";

class multipleFileUpload {
  private files: File[];
  private totalSent: number = 0;
  private totalFilesSizes: number = 0;

  private fileSocket: Socket;

  constructor(files: File[]) {
    this.fileSocket = socketio.socket("/files");
    this.fileSocket.connect();

    this.files = files;
    this.files.forEach((file) => (this.totalFilesSizes += file.size));
  }
  async upload() {
    const {
      store: { progressBarValue },
    } = bots.loadPlugins();

    progressBarValue.value = 0.1;

    for (let i = 0; i < this.files.length; i++) {
      setTimeout(async () => {
        const file = this.files[i] as File;
        await this.sendFileInChunks(file); // Envia o arquivo em chunks de 80KB
      }, 500);
    }

    await new Promise((r) => setTimeout(r, 5000));
    progressBarValue.value = 0;
  }
  private async sendFileInChunks(file: File) {
    const {
      store: { progressBarValue },
    } = bots.loadPlugins();

    const chunkSize = 1024;
    const fileSize = file.size;
    const totalChunks = Math.ceil(fileSize / chunkSize);

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(file.size, start + chunkSize);

      const chunk = file.slice(start, end);
      const arrayBuffer = await chunk.arrayBuffer();
      const currentSize = arrayBuffer.byteLength;

      this.totalSent += currentSize;

      await new Promise<void>((resolve, reject) => {
        setTimeout(() => {
          this.fileSocket.emit(
            "add_file",
            {
              name: file.name,
              chunk: arrayBuffer,
              current_size: currentSize,
            },
            (err: Error | null) => {
              if (err) reject(err);
              else resolve();
            },
          );
        }, 20);
      });

      // Atualiza a progressbar lentamente
      const currentProgress = progressBarValue.value;
      const targetProgress = Math.round((this.totalSent / this.totalFilesSizes) * 100);

      const step = targetProgress > currentProgress ? 1 : -1;

      while (progressBarValue.value !== targetProgress) {
        progressBarValue.value += step;
        await new Promise((r) => setTimeout(r, 20));
      }
    }
  }
}

export default multipleFileUpload;
