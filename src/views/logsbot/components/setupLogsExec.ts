import { useStoreLogsBot } from "@/stores/bot/logs";
import styled from "@vue-styled-components/core";

import { storeToRefs } from "pinia";
import { onMounted, ref } from "vue";

export default function () {
  const { contentRef } = storeToRefs(useStoreLogsBot());
  const SizeCard = ref(500);
  const MinSizeCard = ref(500);
  const CardContent = styled.div.props({ SizeCard: Number, MinSizeCard: Number })`
    max-height: ${(props) => props.SizeCard}px;
    min-height: ${(props) => props.MinSizeCard}px;
    height: 100%;
    display: flex;
    justify-content: center;
  `;

  onMounted(() => {
    if (contentRef.value && contentRef.value?.clientHeight) {
      SizeCard.value = contentRef.value?.clientHeight - 264;
    }

    window.addEventListener("resize", () => {
      if (contentRef.value?.clientHeight) {
        let val = contentRef.value?.clientHeight - 264;
        let minValue = val - 10;
        if (val < 0) {
          val = contentRef.value?.clientHeight;
        }

        if (minValue < 0) {
          minValue = contentRef.value?.clientHeight;
        }

        MinSizeCard.value = minValue;
        SizeCard.value = val;
      }
    });
  });

  return {
    contentRef,
    SizeCard,
    MinSizeCard,
    CardContent,
  };
}
