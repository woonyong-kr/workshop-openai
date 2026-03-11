document.addEventListener("DOMContentLoaded", () => {
  const list = document.querySelector("#message-list");
  const sentinel = document.querySelector("#infinite-sentinel");

  if (!list || !sentinel) {
    return;
  }

  let nextCursor = sentinel.dataset.nextCursor || "";
  let isLoading = false;
  const preloadDistance = 1200;

  const setSentinelText = (message) => {
    sentinel.textContent = message;
  };

  const finish = (message) => {
    nextCursor = "";
    sentinel.dataset.nextCursor = "";
    observer.disconnect();
    setSentinelText(message);
  };

  const shouldPrefetch = () => {
    const rect = sentinel.getBoundingClientRect();
    return rect.top - window.innerHeight <= preloadDistance;
  };

  const loadMore = async () => {
    if (isLoading || !nextCursor) {
      return;
    }

    isLoading = true;
    setSentinelText("메일을 더 불러오는 중입니다...");

    try {
      const url = new URL(sentinel.dataset.feedUrl, window.location.origin);
      url.searchParams.set("cursor", nextCursor);

      const response = await fetch(url.toString(), {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) {
        throw new Error(`Feed request failed: ${response.status}`);
      }

      const payload = await response.json();
      if (payload.html) {
        list.insertAdjacentHTML("beforeend", payload.html);
      }

      nextCursor = payload.next_cursor || "";
      sentinel.dataset.nextCursor = nextCursor;

      if (!nextCursor) {
        finish("모든 메일을 확인했습니다.");
        return;
      }

      setSentinelText("다음 메일을 미리 준비하고 있습니다.");

      if (shouldPrefetch()) {
        window.setTimeout(loadMore, 0);
        return;
      }

      setSentinelText("아래로 조금 더 내리면 다음 메일을 바로 불러옵니다.");
    } catch (error) {
      console.error(error);
      setSentinelText("메일을 더 불러오지 못했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      isLoading = false;
    }
  };

  const observer = new IntersectionObserver(
    (entries) => {
      const isVisible = entries.some((entry) => entry.isIntersecting);
      if (isVisible) {
        loadMore();
      }
    },
    { rootMargin: `${preloadDistance}px 0px` }
  );

  if (nextCursor) {
    observer.observe(sentinel);
    if (shouldPrefetch()) {
      loadMore();
    } else {
      setSentinelText("아래로 조금 더 내리면 다음 메일을 바로 불러옵니다.");
    }
  } else {
    setSentinelText("모든 메일을 확인했습니다.");
  }
});
