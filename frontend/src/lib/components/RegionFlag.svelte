<script lang="ts">
  interface Props {
    regionId: string;
    class?: string;
  }

  import { Globe } from "lucide-svelte";

  let { regionId, class: className = "w-6 h-6" }: Props = $props();
</script>

{#if regionId === "global"}
  <div class={className}><Globe /></div>
{:else if regionId === "us"}
  <img src="/flags/us.svg" alt="US Flag" class={className} />
{:else if regionId === "eu"}
  <img src="/flags/eu.svg" alt="EU Flag" class={className} />
{:else if regionId === "egypt"}
  <img src="/flags/eg.svg" alt="Egypt Flag" class={className} />
{:else if regionId === "saudi"}
  <img src="/flags/sa.svg" alt="Saudi Arabia Flag" class={className} />
{:else if regionId === "africa"}
  <!-- Africa SVG Icon -->
  <svg
    viewBox="0 0 512 512"
    xmlns="http://www.w3.org/2000/svg"
    fill="#ffffff"
    stroke="#ffffff"
    ><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g
      id="SVGRepo_tracerCarrier"
      stroke-linecap="round"
      stroke-linejoin="round"
    ></g><g id="SVGRepo_iconCarrier"
      ><path
        fill="#ffffff"
        d="M201.56 19.495l-87.79 9.131-73.745 94.814v52.676l56.186 61.805 64.615-13.344 49.164 9.832-10.535 37.926 33.711 61.103-16.855 42.842 39.79 116.225 53.62-8.768 49.164-55.484 4.213-38.629 31.605-23.879-6.322-69.531 83.594-106.994-51.989 7.263-79.363-138.359-125.016-8.428-14.046-30.2zm252.346 319.8l-14.402 20.86-13.408.496c-11.849 24.321-12.598 38.019-13.907 66.547l17.383 4.471 21.852-52.147 2.482-40.226z"
      ></path></g
    ></svg
  >
{:else if regionId === "middleeast"}
  <img src="/flags/middle-east.svg" alt="Saudi Arabia Flag" class={className} />
{:else}
  <div class={className}>🌐</div>
{/if}

<style>
  div {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5em;
    line-height: 1;
  }

  img {
    object-fit: contain;
    border-radius: 2px;
  }
</style>
