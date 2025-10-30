import { storeToRefs } from "pinia";
import type { Socket } from "socket.io-client";

class FileUploader {
  public FormBot: FormData;
  private totalSent: number;
  private chunkSize: number;
  public fileSocket?: Socket = undefined;

  constructor() {
    this.totalSent = 0;
    this.chunkSize = 1024 * 80;
    this.fileSocket = socketio.socket("/files");

    this.fileSocket?.connect();
    this.FormBot = new FormData();
  }

  public async uploadXlsx(file: File | undefined): Promise<void> {
    this.totalSent = 0;

    if (file) {
      await this.uploadInChunks(file, file.size);

      // Notifica o enio
      this.FormBot.append("xlsx", file);
      this.FormBot.append("file_sid", this.fileSocket?.id as string);
      this.clearProgressBar(`Arquivo ${file.name} carregado!`);
    }
  }
  public async uploadMultipleFiles(FileList: File[] | undefined): Promise<void> {
    this.totalSent = 0;
    if (FileList) {
      const totalFilesSizes = FileList.reduce((acc, f) => acc + f.size, 0);
      for (const file of FileList) {
        await this.uploadInChunks(file, totalFilesSizes);

        // Notifica o enio
        notify.show({
          title: "Mensagem",
          message: `Arquivo ${file.name} carregado!`,
          type: "info",
          duration: 5000,
        });
      }

      this.FormBot.append("outros_arquivos", FileList.toString());
      this.FormBot.append("outros_arquivos_sid", this.fileSocket?.id as string);
      this.clearProgressBar(`Seus ${FileList.length} foram carregados!`);
    }
  }

  private async uploadInChunks(file: File, totalSize: number) {
    const totalChunks = Math.ceil(file.size / this.chunkSize);
    for (let i = 0; i < totalChunks; i++) {
      const start = i * this.chunkSize;
      const end = Math.min(file.size, start + this.chunkSize);
      console.log(i);
      const chunk = file.slice(start, end);
      const arrayBuffer = await chunk.arrayBuffer();
      const currentSize = arrayBuffer.byteLength;

      this.totalSent = this.totalSent + currentSize;

      await this.uploadToSocketIo(file, arrayBuffer, currentSize);
      await this.updateProgressBar(this.totalSent, totalSize);

      if (end >= totalSize) {
        break;
      }
    }
  }

  private async uploadToSocketIo(file: File, arrayBuffer: ArrayBuffer, currentSize: number) {
    await new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        this.fileSocket?.emit(
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
      }, 20); // delay envio de cada chunk
    });
  }

  private async updateProgressBar(totalSent: number, totalBytes: number) {
    // Ref da progressBar
    const { progressBarValue } = storeToRefs(botStore());

    // Target Progress
    const targetProgress = Math.round((totalSent / totalBytes) * 100);

    // currentProgress
    const currentProgress = progressBarValue.value;

    // step
    const step = targetProgress > currentProgress ? 1 : -1;
    while (progressBarValue.value !== targetProgress) {
      progressBarValue.value += step;
      await new Promise((r) => setTimeout(r, 20));
    }
  }

  private async clearProgressBar(message: string) {
    const { progressBarValue } = storeToRefs(botStore());
    notify.show({
      title: "Sucesso",
      message: message,
      type: "success",
      duration: 5000,
    });
    await new Promise((r) => setTimeout(r, 2000));
    progressBarValue.value = 0;
  }
}

export default FileUploader;
